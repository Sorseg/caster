from database import *

def create(session):
    #populate tables:
    if not session.query(User).filter_by(login ='sors').count():
        d = CrTemplate(cls='drakonian', model='drak1')
        sors = User(login='sors', pwd ='asdf2')
        drak = Creature(d)
        drak.char = '@'
        drak.name = "Malfoy"
        sors.creatures = [drak]
        session.add(sors)
        
    if not session.query(User).filter_by(login = 'demoth').count():
        demoth = User(login='demoth', pwd = 'asdf')
        k = CrTemplate(cls='kob', model='kob1')
        kob = Creature(k)
        mer = Creature(k)
        kob.name = "Kamui"
        mer.name = "Rorkaloler"
        kob.char='&'
        mer.char='M'
        demoth.creatures = [kob, mer]
        session.add(demoth)

    if not session.query(Location).filter_by(name ='cave').filter_by(id = 1).count():
        cave = Location(name = 'cave', id = 1)
        cells = []
        map = open('maps/1.map').read()
        for y, line in enumerate(map.split('\n')):
            for x, symb in enumerate(line):
                c = Cell(coords = (x,y), type = ('floor' if symb == '.' else 'wall'))
                cells.append(c)
        cave.cells = {c.coords:c for c in cells}
        session.add(cave)
        
    if not session.query(Weapon).filter_by(name='sword').count():
        t = WeaponTemplate()
        t.name = 'sword'
        t.min_damage = 1
        t.max_damage = 3
        t.model = 'sword'
        session.add(t)
        sw = Weapon(t)
        sw.char=')'
        sw.location = cave
        sw.coords = (3, 3)
        session.add(sw)
                
    session.commit()
    
def create_test_data(session):
    pass
#TODO: migrate test data from prev function

