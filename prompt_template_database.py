from sqlalchemy import create_engine, MetaData, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from sqlalchemy import asc

# Define the SQLAlchemy base
Base = declarative_base()

# Define the PromptTemplate model
class PromptTemplate(Base):
    __tablename__ = 'prompt_templates'

    id = Column(String, primary_key=True)
    topic = Column(String)
    name = Column(String)
    purpose = Column(String)
    template = Column(Text)
    def __init__(self, topic, name, purpose, template):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.name = name
        self.purpose = purpose
        self.template = template
   
   
        
    @staticmethod
    def get_by_name(session,template_name):
        selected_template = (
            session.query(PromptTemplate)
            .filter_by(name=template_name)
            .first()
        )
        return selected_template
        
        
    @staticmethod
    def get_topics(session):
         return [result[0] for result in session.query(PromptTemplate.topic).distinct().order_by(asc(PromptTemplate.topic))]
        
    @staticmethod 
    def get_all_templates(session):
         return session.query(PromptTemplate).order_by(asc(PromptTemplate.name)).all()


    @staticmethod 
    def get_templates_by_topic(session, topic):
        return session.query(PromptTemplate).filter_by(topic=topic).order_by(asc(PromptTemplate.name)).all()

# Define the database connection
engine = create_engine('sqlite:///prompt_templates.db')

# Create tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()