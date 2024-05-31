"""
PromptTemplate Module
======================

This module defines the `PromptTemplate` class and provides utility methods to interact with
the `prompt_templates` table in a SQLite database using SQLAlchemy.

Classes:
    PromptTemplate: A SQLAlchemy ORM class for the `prompt_templates` table.

Functions:
    create_database: Creates the `prompt_templates` table in the database.
    get_session: Creates and returns a new SQLAlchemy session.
"""
import uuid
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.types import Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc

# Define the SQLAlchemy base
Base = declarative_base()


class PromptTemplate(Base):
    """
    A SQLAlchemy ORM class representing the `prompt_templates` table.

    Attributes:
        id (str): The primary key, a unique identifier for each prompt template.
        topic (str): The topic of the prompt template.
        name (str): The name of the prompt template.
        purpose (str): The purpose of the prompt template.
        template (str): The text content of the prompt template.
        use_web_search (bool): Indicates whether web search is used in the template.

    Methods:
        get_by_name(session, template_name): Fetches a template by its name.
        get_topics(session): Retrieves distinct topics from the templates.
        get_all_templates(session): Fetches all templates, ordered by name.
        get_templates_by_topic(session, topic): Fetches templates filtered by topic, ordered by name.
    """
    __tablename__ = 'prompt_templates'

    id = Column(String, primary_key=True)
    topic = Column(String)
    name = Column(String)
    purpose = Column(String)
    template = Column(Text)
    use_web_search = Column(Boolean)
    def __init__(self, topic, name, purpose, template, use_web_search):
        """
        Initializes a new instance of PromptTemplate.

        Args:
            topic (str): The topic of the prompt template.
            name (str): The name of the prompt template.
            purpose (str): The purpose of the prompt template.
            template (str): The text content of the prompt template.
            use_web_search (bool): Indicates whether web search is used in the template.
        """
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.name = name
        self.purpose = purpose
        self.template = template
        self.use_web_search = use_web_search 
        
    @staticmethod
    def get_by_name(session,template_name):
        """
        Fetches a prompt template by its name.

        Args:
            session (Session): The SQLAlchemy session.
            template_name (str): The name of the prompt template to fetch.

        Returns:
            PromptTemplate: The prompt template with the given name, or None if not found.
        """
        selected_template = (
            session.query(PromptTemplate)
            .filter_by(name=template_name)
            .first()
        )
        return selected_template
        
        
    @staticmethod
    def get_topics(session):
         """
        Retrieves distinct topics from the prompt templates.

        Args:
            session (Session): The SQLAlchemy session.

        Returns:
            list: A list of distinct topics.
        """
         return [result[0] for result in session.query(PromptTemplate.topic).distinct().order_by(asc(PromptTemplate.topic))]
        
    @staticmethod 
    def get_all_templates(session):
        """
        Fetches all prompt templates, ordered by name.

        Args:
            session (Session): The SQLAlchemy session.

        Returns:
            list: A list of all prompt templates.
        """
        return session.query(PromptTemplate).order_by(asc(PromptTemplate.name)).all()


    @staticmethod 
    def get_templates_by_topic(session, topic):
        """
        Fetches prompt templates filtered by topic, ordered by name.

        Args:
            session (Session): The SQLAlchemy session.
            topic (str): The topic to filter the prompt templates by.

        Returns:
            list: A list of prompt templates for the specified topic.
        """
        return session.query(PromptTemplate).filter_by(topic=topic).order_by(asc(PromptTemplate.name)).all()

# Define the database connection
engine = create_engine('sqlite:///prompt_templates.db')

# Create tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()