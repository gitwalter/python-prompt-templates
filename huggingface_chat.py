"""
HuggingChatWrapper Module
=========================

This module defines the `HuggingChatWrapper` class to interact with the Hugging Face chat models
via the HugChat API.

Classes:
    HuggingChatWrapper: A wrapper class to manage Hugging Face chat models and interactions.

"""

import streamlit as st
from hugchat import hugchat
from hugchat.login import Login

class HuggingChatWrapper:
    """
    A wrapper class to manage Hugging Face chat models and interactions.

    Attributes:
        email (str): The email used to log in to Hugging Face.
        password (str): The password used to log in to Hugging Face.
        cookie_path_dir (str): The directory path to save cookies.
        cookies (RequestsCookieJar): The cookies obtained after logging in.
        chatbot (hugchat.ChatBot): An instance of the HugChat ChatBot.
        models (list): A list of available language models.
        model_names (list): A list of names of available language models.

    Methods:
        get_available_models(): Returns the names of available language models.
        switch_model(model_name): Switches the current model to the specified one.
        chat(query, web_search): Executes a chat query and returns the response.
        reset(): Resets the conversation history.
        delete_all(): Deletes all conversations.
    """
    
    def __init__(self, email=None, password=None):
        """
        Initializes a new instance of HuggingChatWrapper.

        Args:
            email (str, optional): The email used to log in to Hugging Face. Defaults to None.
            password (str, optional): The password used to log in to Hugging Face. Defaults to None.
        """
        self.email = st.secrets.get("HF_EMAIL")
        self.password = st.secrets.get("HF_PWD")                        

        # Log in to Hugging Face and grant authorization to Hugging Chat
        self.cookie_path_dir = "./cookies/"
        sign = Login(self.email, self.password)
        self.cookies = sign.login(cookie_dir_path=self.cookie_path_dir, save_cookies=True)
        
        # Create ChatBot
        self.chatbot = hugchat.ChatBot(cookies=self.cookies.get_dict())

        self.models = self.chatbot.get_available_llm_models()
        self.model_names = [model.name for model in self.models]

    def get_available_models(self):
        """
        Returns the names of available language models.

        Returns:
            list: A list of names of available language models.
        """
        return self.model_names        

    def switch_model(self, model_name):
        """
        Switches the current model to the specified one.

        Args:
            model_name (str): The name of the model to switch to.
        """
        for idx, model in enumerate(self.models):
            if model.name == model_name:
                model_index = idx
        
        self.chatbot.switch_llm(model_index)

    def chat(self, query, web_search):
        """
        Executes a chat query and returns the response.

        Args:
            query (str): The chat query.
            web_search (bool): Whether to use web search in the chat query.

        Returns:
            str: The response from the chat query.
        """
        query_result = self.chatbot.chat(query, web_search=web_search)
        return query_result
    
    def reset(self):
        """
        Resets the conversation history.
        """
        conversations = self.chatbot.get_conversation_list()
        for conversation in conversations:
            self.chatbot.delete_conversation(conversation)                    
        
    def delete_all(self):
        """
        Deletes all conversations.
        """
        self.chatbot.delete_all_conversations()
