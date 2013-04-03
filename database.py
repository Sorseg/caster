'''TODO LIST:
- cascades
- items, item types
- monsters, monster types
- size should be one number
- requests should not be in db at all
'''

from sqlalchemy import Column as col, Integer, String, CHAR, Float,\
                        ForeignKey, create_engine, select

from sqlalchemy.orm import relationship, sessionmaker, backref, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from collections import defaultdict
from settings import *
from twisted.internet.defer import DeferredLock, Deferred, maybeDeferred

engine = create_engine(DATABASE_CONNECTION, echo=True)
'''
from sqlalchemy.pool import StaticPool
engine = create_engine('sqlite:///:memory:',
                    connect_args={'check_same_thread':False},
                    poolclass=StaticPool,
                    echo=False)
'''
Session = sessionmaker(bind=engine)

class NamedLock(DeferredLock):
    
    def acquire(self, name='noname'):
        d = Deferred(canceller=self._cancelAcquire)
        d.name = name
        if self.locked:
            self.waiting.append(d)
        else:
            self.locked = True
            d.callback(self)
        return d
    
    def run(*args, **kwargs): #@NoSelf
        """ Overriden method from twisted to use name """
        if len(args) < 3:
            if not args:
                raise TypeError("run() takes at least 3 arguments")
        self, f, name = args[:3]
        args = args[3:]

        def execute(ignoredResult):
            d = maybeDeferred(f, *args, **kwargs)
            d.addBoth(self._releaseAndReturn)
            return d

        d = self.acquire(name)
        d.addCallback(execute)
        d.addErrback(lambda i:None)
        return d

class Handler(object):

    def __init__(self):
        self.session = Session()

    def login(self, login, md5, cr_id = None):
        s = self.session
        q = s.query(User).filter((User.login == login) &
                                 (User.pwd == md5))
        if q.count():
            creatures = q.one().creatures
            if not cr_id:
                return creatures
            cr = {str(i.id):i for i in creatures}
            return [cr.get(cr_id, None)]


    def draw_map(self, loc_id):
        s = self.session
        l = s.query(Location).filter_by(id=loc_id).one()
        maxx, maxy = l.dimensions
        objects = l.objects
        objects = {o.cell.coords:o for o in objects}
        cells = {c.coords:c for c in l.cells}
        map = ''
        for y in range(maxy):
            line = ''
            for x in range(maxx):
                line += objects.get((x,y),cells[(x,y)]).char
            map += line + '\n'
            line = ''
        return map

    def get_location(self, loc_id):
        return self.session.query(Location).get(loc_id)
    
    def refresh(self, object):
        return self.session.query(type(object)).get(object.id)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ''' rollback or commit '''
        if args[0]:
            print "NOT COMMITTED!", args
        else:
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
        assert obj.id, "Assigning to object without id"
        self.dict[obj.id] = value
        

class Coord(tuple):
    
    def __add__(self, c):
        return Coord([i + j for i, j in zip(self, c)])

    def __str__(self):
        return "{},{}".format(*self)
    
    def dist((x1,y1),(x2,y2)): #@NoSelf
        return ((x2-x1)**2 + (y2-y1)**2)**0.5


class Space(object):
    def __init__(self, coord, size):
        self.coord = coord
        self.size = size
        
    def fits(self, new_pos, cells):
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

    def would_coords(self, pos):
        return {Coord(pos) + (x, y)\
        for x in range(self.size) for y in range(self.size)}

    def fits(self, cell):
        #TODO:
        pass

    @property
    def coords(self):
        return Coord((self.xpos, self.ypos))
    
    @coords.setter
    def coords(self, coords):
        self.xpos, self.ypos = coords



class Creature(Object):
    __tablename__ = 'creatures'
    
    def __init__(self, template):
        assert isinstance(template, CrTemplate), ("creature can be created"
                                                  " only using CrTemplate,"
                                                  " not "+str(type(template)))
        self.template = template

    __mapper_args__ = {'polymorphic_identity': 'creature'}
        
    id = col(Integer, ForeignKey("objects.id"), primary_key=True)
    user_login = col(String(100), ForeignKey("users.login"))
    sight = col(Integer, default = 6) # radius of sight
    visible_cells=association_proxy('visibilities', 'cell')
    max_life = col(Integer, default = 20)
    
    template_id = col(Integer, ForeignKey("crtemplates.id"))
    template = relationship("CrTemplate")
    
    model = association_proxy('template','model')
    name = association_proxy('template','name')
    descr = association_proxy('template','descr')
    equipped_id = col(Integer, ForeignKey("items.id", use_alter=True, name="fk_equipped"))
    equipped = relationship("Item", primaryjoin="Creature.equipped_id==Item.id", uselist=False, post_update=True,
                            backref=("equipped_by"))
    
    @property
    def damage(self):
        #if self.equipped:
        #   return self.equipped.damage
        return 1
    
    def __str__(self):
        return "({}){}:{}".format(self.id, self.user_login, self.name)

    __repr__ = __str__


class CrTemplate(Base):
    __tablename__ = 'crtemplates'

    id = col(Integer, primary_key=True)
    name = col(String(200))
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
    
    locks = defaultdict(NamedLock)
    lock = NonDbData(locks)
    
    updaters = {}
    updater = NonDbData(updaters)
    
    all_requests = defaultdict(list)
    requests = NonDbData(all_requests)

    id = col(Integer, primary_key=True)
    name = col(String(50))
    cells = relationship(Cell, collection_class=attribute_mapped_collection("coords"), backref="location")

    @property
    def dimensions(self):
        x = max([c[0] for c in self.cells])
        y = max([c[1] for c in self.cells])
        return (x+1,y+1)
    
    objects = relationship(Object, collection_class=attribute_mapped_collection("coords"))
    
#    @property
#    def items(self):
#        items = defaultdict(list)
#        for o in self.objects_list:
#            if isinstance(o, Item):
#                items[o.coords].append(o)
#        return items
#    
#    @property
#    def creatures(self):
#        items = defaultdict(list)
#        for o in self.objects_list:
#            if isinstance(o, Creature):
#                items[o.coords].append(o)
#        return items
    
    def draw(self):
        data = ''
        chars = {}
        chars.update({c:o.char for c,o in self.cells.items()})
        for y in range(self.dimensions[1]):
            line = ''
            for x in range(self.dimensions[0]):
                line += chars.get((x,y),' ')
            data += line + '\n'
            
        return data 

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Location:{}({})>'.format(self.name,self.id)


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
    Base.metadata.create_all(engine)
    import create_data
    create_data.create(session)
    create_data.create_test_data(session)

# create tables here:
if __name__ == '__main__':
    create()
