import streamlit as st
from hugchat import hugchat
from hugchat.login import Login

class HuggingChatWrapper:
    def __init__(self, email=None, password=None):
        # Load environment variables from .env file
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
        # Get available language models
        return self.model_names        

    def switch_model(self, model_name):        
        for idx, model in enumerate(self.models):
            if model.name == model_name:
                model_index = idx
        
        self.chatbot.switch_llm(model_index)

    def chat(self, query, web_search):
        # Execute a chat query and return the response
        # self.chatbot.new_conversation(switch_to = True)
        query_result = self.chatbot.chat(query, web_search=web_search)
        return query_result
    
    def reset(self):
        conversations = self.chatbot.get_conversation_list()
        for conversation in conversations:
            self.chatbot.delete_conversation(conversation)                    
        
    def delete_all(self):
        self.chatbot.delete_all_conversations()