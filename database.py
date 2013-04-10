'''TODO LIST:
- cascades
- items, item types
- monsters, monster types
- size should be one number
- requests should not be in db at all
'''

from collections import defaultdict
from settings import *
from sqlalchemy import Column as col, Integer, String, CHAR, Float, ForeignKey, \
    create_engine, select, BigInteger
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, sessionmaker, backref, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import UniqueConstraint
from threading import RLock
import logging


engine = create_engine(DATABASE_CONNECTION, echo=True)
Session = sessionmaker(bind=engine, expire_on_commit = False)


class Handler(object):

    def __init__(self):
        self.session = Session()

    def login(self, login, passw):
        s = self.session
        q = s.query(User).filter((User.login == login) &
                                 (User.pwd == passw))
        if q.count():
            creatures = q.one().creatures
            return creatures
    
    def refresh(self, object, id = None):
        q = self.session.query(type(object))
        if id:
            return q.get(id)
        else:
            return q.get(object.id)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ''' rollback or commit '''
        if not args[0]:
            self.session.commit()
        self.session.close()

    def __del__(self):
        self.session.close()


class NonDbData(object):
    
    def __init__(self, dic):
        self.dict = dic

    def __get__(self, obj, type):
        return obj.id and self.dict.get(obj.id, None)

    def __set__(self, obj, value):
        if not obj.id:
            logging.error("Assigning to object without id")
            return
        self.dict[obj.id] = value


class Coord(tuple):

    def __add__(self, c):
        return Coord([i + j for i, j in zip(self, c)])

    def __str__(self):
        return "{},{}".format(*self)

    def dist(x1_y1,x2_y2): #@NoSelf
        return ((x2-x1)**2 + (y2-y1)**2)**0.5


class Space(object):
    circle_approx = [
                      (),
                      ('#'),
                      
                      ('##',
                       '##'),
                              
                      ('###',
                       '###',
                       '###'),
                              
                      (' ## ',
                       '####',
                       '####',
                       ' ## '),
                      
                      (' ### ',
                       '#####',
                       '#####',
                       '#####',
                       ' ### ',
                      )
                              ]
    
    def __init__(self, coord, size):
        self.coord = coord
        self.size = size
        
    def fits(self, new_pos, cells):
        #TODO
        pass


############### MAPPING ##############

Base = declarative_base()

class Object(Base):
    __tablename__ = 'objects'
    
    id = col(Integer, primary_key=True)
    type = col(String(20))
    __mapper_args__ = {'polymorphic_on': type}
    
    loc_id = col(Integer, ForeignKey("locations.id"))
    location = relationship("Location", backref="objects_list")
    xpos = col(Integer)
    ypos = col(Integer)
    size = col(Integer, default = 1)
    char = col(CHAR, default='?')

    @property
    def coords(self):
        return Coord((self.xpos, self.ypos))
    
    @coords.setter
    def coords(self, coords):
        self.xpos, self.ypos = coords


class Creature(Object):
    __tablename__ = 'creatures'
    
    def __init__(self, template):
        if not isinstance(template, CrTemplate):
            raise TypeError("creature can be created"
                                                  " only using CrTemplate,"
                                                  " not "+str(type(template)))
            
        self.template = template

    __mapper_args__ = {'polymorphic_identity': 'creature'}
        
    id = col(Integer, ForeignKey("objects.id"), primary_key=True)
    user_login = col(String(100), ForeignKey("users.login"))
    sight = col(Integer, default = 6) # radius of sight

    max_life = col(Integer, default = 20)
    #TODO: life, mana?
    template_id = col(Integer, ForeignKey("crtemplates.id"))
    template = relationship("CrTemplate")
    
    model = association_proxy('template','model')
    name = col(String(100), nullable = False, unique = True)
    cls = association_proxy('template','cls')
    descr = association_proxy('template','descr')
    equipped_id = col(Integer, ForeignKey("items.id", use_alter=True, name="fk_equipped"))
    equipped = relationship("Item", primaryjoin="Creature.equipped_id==Item.id", uselist=False, post_update=True,
                            backref=("equipped_by"))
    
    @property
    def damage(self):
        #if self.equipped:
        #   return self.equipped.damage
        return 1
    
    @property
    def short_info(self):
        return {"model":self.model,
                "id":self.id,
                "name":self.name,
                "cls":self.cls}
    
    def __str__(self):
        return "({}){}:{}".format(self.id, self.user_login, self.name)

    __repr__ = __str__


class CrTemplate(Base):
    __tablename__ = 'crtemplates'

    id = col(Integer, primary_key=True)
    cls = col(String(200))
    descr = col(String(200))
    model = col(String(200))
    str = col(Integer)
    dex = col(Integer)
    int = col(Integer)
    # creatureattrs =  relationship("CrTemplAttribute") TODO
    life = col(Integer)
    mana = col(Integer)


class ItemTemplate(Base):
    __tablename__ = 'itemtemplates'
    
    id = col(Integer, primary_key=True)
    name = col(String(200))
    descr = col(String(200))
    model = col(String(200))
    weight = col(Float)
    type = col(String(20))
    max_dur = col(Integer)
    __mapper_args__ = {'polymorphic_on': type}
    #requirements will be in attributes
    #itemattrs =  relationship("ItemTemplAttribute") TODO


class WeaponTemplate(ItemTemplate):
    __tablename__ = 'weapontemplates'
    __mapper_args__ = {'polymorphic_identity': 'weapon'}
    
    id = col(Integer, ForeignKey(ItemTemplate.id), primary_key=True)
    min_damage = col(Integer)
    max_damage = col(Integer)
    
    
class User(Base):
    __tablename__ = 'users'
    
    login = col(String(100), primary_key=True)
    pwd = col(String(32))
    creatures = relationship(Creature, backref="user")
    admin = col(CHAR(1))

    def __str__(self):
        return self.login

    def __repr__(self):
        return '<User({})>'.format(self.login)


class Cell(Base):
    
    WALL = 0
    FLOOR = 1
    WATER = 2
    LAVA = 3
    
    __tablename__ = 'cells'
    __table_args__ = (
        UniqueConstraint('xpos', 'ypos', 'loc_id', name='cells_uc'),)

    id = col(Integer, primary_key=True)
    xpos = col(Integer)
    ypos = col(Integer)
    loc_id = col(Integer, ForeignKey("locations.id"))
    char = col(CHAR(1))
    type = col(Integer)

    @property
    def coords(self):
        return Coord((self.xpos, self.ypos))

    @coords.setter
    def coords(self, c):
        self.xpos, self.ypos = c

    def __str__(self):
        return self.char

    def __repr__(self):
        return "<Cell {} ({},{}):{}>".format(self.char, self.xpos, self.ypos, self.loc_id)


class Item(Object):
    __tablename__='items'
    
    id = col(Integer, ForeignKey('objects.id'), primary_key = True)
    name = association_proxy('template','name')
    descr = association_proxy('template','descr')
    model = association_proxy('template','model')
    weight = col(Float)
    dur = col(Integer)
    max_dur = col(Integer)
    bagged_by_id = col(Integer, ForeignKey(Creature.id))
    bagged_by = relationship(Creature, backref='inventory', 
                            primaryjoin="Item.bagged_by_id==Creature.id")


class Location(Base):
    __tablename__ = 'locations'
    
    current_turn = col(BigInteger, nullable = False, default = 0)

    id = col(Integer, primary_key=True)
    name = col(String(50))
    cells = relationship(Cell, collection_class=attribute_mapped_collection("coords"), backref="location")

    @property
    def dimensions(self):
        x = max([c[0] for c in self.cells])
        y = max([c[1] for c in self.cells])
        return (x+1, y+1)
    
    objects = relationship(Object, collection_class=attribute_mapped_collection("coords"))
    
    #TODO: optmimze
    @property
    def items(self):
        items = defaultdict(list)
        for o in self.objects.values():
            if isinstance(o, Item):
                items[o.coords].append(o)
        return items
    
    @property
    def creatures(self):
        items = defaultdict(list)
        for o in self.objects.values():
            if isinstance(o, Creature):
                items[o.coords].append(o)
        return items

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Location:{}({})>'.format(self.name, self.id)


class Weapon(Item):
    __tablename__='weapons'
    __mapper_args__ = {'polymorphic_identity': 'weapon'}
    
    id = col(Integer, ForeignKey('items.id'), primary_key = True)
    template_id = col(Integer, ForeignKey(WeaponTemplate.id))
    template = relationship(WeaponTemplate)
    min_damage = col(Integer, nullable=False)
    max_damage = col(Integer, nullable=False)
    
    def __init__(self, template):
        assert isinstance(template, WeaponTemplate), "wrong argument to init"
        super(Weapon, self).__init__()
        self.template = template
        self.min_damage = template.min_damage
        self.max_damage = template.max_damage
        self.dur = self.max_dur = template.max_dur


def destroy():
    session = Session()
    session.execute("drop database if exists caster;")
    session.execute("create database caster;")
    session.commit()

def create():
    session = Session()
    session.execute("use caster;")
    Base.metadata.create_all(engine)
    import create_data
    create_data.create(session)
    create_data.create_test_data(session)

# create tables here:
if __name__ == '__main__':
    destroy()
    create()
