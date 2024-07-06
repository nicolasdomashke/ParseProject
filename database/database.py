from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def save_data_to_db(items):
    print(len(items))
    for item in items:
        vacancy = Vacancy(
            id=item['id'],
            name=item['name'],
            employer_name=item['employer']['name'],
            area=item['area']['name'],
            url=item['alternate_url'],
            description=item['snippet'].get('responsibility', '')
        )
        session.merge(vacancy)
    session.commit()

def get_vacancies(filters={}):
    query = session.query(Vacancy)
    if filters['area'] != "-":
        query = query.filter(Vacancy.area.ilike(f"%{filters['area']}%"))
    if filters['employer'] != "-":
        query = query.filter(Vacancy.employer_name.ilike(f"%{filters['employer']}%"))
    if 'text' in filters:
        query = query.filter(Vacancy.name.ilike(f"%{filters['text']}%"))
    return query.all()

class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    employer_name = Column(String)
    area = Column(String)
    url = Column(String)
    description = Column(Text)

engine = create_engine('sqlite:///vacancies.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
