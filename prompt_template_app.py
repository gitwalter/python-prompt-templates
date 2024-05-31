"""
Streamlit Application for Prompt Template Management and Chat Interaction with HuggingFace API

This application provides a user interface for managing prompt templates and interacting with a language model (LLM) using these templates. The application has the following capabilities:

- **Create and Edit Prompt Templates**: Users can create new prompt templates, edit existing ones, or delete templates.
- **Use Templates to Generate Prompts**: Users can select a template, input variables, and generate prompts that are sent to the LLM for processing.
- **Display Prompting Principles**: Users can view principles and guidelines for effective prompting.

Key Components:
1. **Streamlit Input Fields**: Dynamic creation of input fields for template variables.
2. **Template Management**: Functions to retrieve, create, update, and delete templates from a database.
3. **HuggingFace API Integration**: Use of `HuggingChatWrapper` to interact with language models hosted on HuggingFace via the HuggingChat API.
4. **Prompt Template Handling**: Use of `ChatPromptTemplate` to format and process input data for the LLM.

Functions:
    - `create_input_fields(variables)`: Creates Streamlit input fields for string variables.
    - `get_templates()`: Retrieves templates by topic from the database.
    - `get_chat_wrapper()`: Returns an instance of `HuggingChatWrapper`, cached for resource efficiency.
    - `main()`: Main function to run the Streamlit app.

Workflow:
- **Template Editing**: Users select "Edit Template" to modify existing templates or create new ones. Input fields for template details (name, topic, purpose, template content) are provided, along with options to save or delete the template.
- **Using Templates**: Users select "Use Template" to pick a template and provide input variables. The formatted prompt is sent to the selected model via the HuggingChat API, and the response is displayed along with any web search sources used.
- **Prompting Principles**: Users can view predefined principles for creating effective prompts.

Dependencies:
- `streamlit`: For creating the web interface.
- `langchain.prompts.ChatPromptTemplate`: For handling prompt templates.
- `prompt_template_database.session` and `prompt_template_database.PromptTemplate`: For database interactions.
- `text_definitions.prompting_principles`: For displaying prompting guidelines.
- `huggingface_chat.HuggingChatWrapper`: For interacting with the HuggingFace LLM API.

Usage:
- Run the script in a Streamlit environment to start the application.
- Navigate through the sidebar options to manage templates or interact with the LLM.

"""
import streamlit as st
from prompt_template_database import session, PromptTemplate
from text_definitions import prompting_principles
from langchain.prompts import ChatPromptTemplate
from huggingface_chat import HuggingChatWrapper

# Function to create Streamlit input fields for string variables
def create_input_fields(variables):
    inputs = {}
    for variable in variables:
        var_name = variable
        inputs[var_name] = st.text_input(var_name)
    return inputs


# retrieve templates by topic from db
def get_templates():
    topics = PromptTemplate.get_topics(session)
    selected_topic = st.sidebar.selectbox(
        "Select Topic", ["All"] + topics
)  # Add dropdown for selecting topic
    if selected_topic == "All":
        templates = PromptTemplate.get_all_templates(session)
    else:
        templates= PromptTemplate.get_templates_by_topic(session,selected_topic)
        
    return templates

@st.cache_resource
def get_chat_wrapper():
    return HuggingChatWrapper()

# Main function to run the Streamlit app
def main():
    st.sidebar.title("Select Action")

    action = st.sidebar.radio(
        "Action", ["Edit Template", "Use Template", "Prompting Principles"]
    )

    if action == "Prompting Principles":
        st.markdown(prompting_principles)
        

    if action == "Edit Template":
        st.sidebar.title("Select Prompt Template")
        
        templates = get_templates()
        template_names = ["New Template"]  # Make "New Template" the first option
        template_names.extend([template.name for template in templates])

        selected_template_name = st.sidebar.selectbox("Template", template_names)

        if selected_template_name == "New Template":
            selected_template = None
            st.empty()            
            name = st.text_input("Name")
            topic = st.text_input("Topic")
            purpose = st.text_area("Purpose")
            use_web_search = st.checkbox("Use Web Search")
            template = st.text_area(
                "Template", height=250
            )  # Make the text area expand vertically
            if st.button("Save New Template"):
                if not topic:
                    st.error("Please enter a topic for the template!")
                if not name:
                    st.error("Please enter a name for the template!")
                else:
                    if name in template_names[1:]:
                        st.error("A template with this name already exists!")
                    else:
                        new_template = PromptTemplate(
                            topic=topic, 
                            name=name, 
                            purpose=purpose,
                            template=template,
                            use_web_search=use_web_search
                        )
                        session.add(new_template)
                        session.commit()
                        st.success("Template saved successfully!")
        else:
            selected_template = PromptTemplate.get_by_name(session,selected_template_name)
            if selected_template:
                topic = st.text_input("Topic", value=selected_template.topic)
                name = st.text_input("Name", value=selected_template.name)
                purpose = st.text_area("Purpose", value=selected_template.purpose)
                use_web_search = st.checkbox("Use Web Search", value=selected_template.use_web_search)
                template = st.text_area(
                    "Template", value=selected_template.template, height=400
                )  # Make the text area expand vertically
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save", key="save_button"):
                        if not topic:
                            st.error("Please enter a topic for the template!")
                        if not name:
                            st.error("Please enter a name for the template!")
                        else:
                            if (
                                name != selected_template_name
                                and name in template_names[1:]
                            ):
                                st.error("A template with this name already exists!")
                            else:
                                selected_template.name = name
                                selected_template.purpose = purpose
                                selected_template.use_web_search = use_web_search
                                selected_template.template = template
                                session.commit()
                                st.success("Changes saved successfully!")
                with col2:
                    if st.button("Delete", key="delete_button"):
                        if selected_template:
                            session.delete(selected_template)
                            session.commit()
                            st.success("Template deleted successfully!")
    elif action == "Use Template":
        st.sidebar.title("Select Prompt Template")
        templates = get_templates()
        template_names = [template.name for template in templates]

        selected_template_name = st.sidebar.selectbox("Template", template_names)

        selected_template = PromptTemplate.get_by_name(session,selected_template_name)        

        if selected_template:
            st.write(f"Topic: {selected_template.topic}")
            st.write(f"Name: {selected_template.name}")
            st.write(f"Purpose: {selected_template.purpose}")
            st.write(f"Template: {selected_template.template}")


            chat_wrapper = get_chat_wrapper()
            model_names = chat_wrapper.get_available_models()
            chat_wrapper.reset()
            
         # Display available models in selectbox            
            model_name = st.sidebar.selectbox("Select Model", model_names)
                        
            prompt_template = ChatPromptTemplate.from_template(
                selected_template.template
            )
            input_variables = prompt_template.messages[0].prompt.input_variables
            inputs = create_input_fields(input_variables)

            display_query_result = False

            col1, col2 = st.columns(2)
            with col1:
                use_web_search = st.checkbox("Use Web Search", selected_template.use_web_search)                            
                        
            with col2:
                keep_chat_on_server = st.checkbox("Keep chat on Server")                    
                       
            if st.button("Submit"):                
                input_values = {}
                for var_name, var_value in inputs.items():
                    input_values[var_name] = var_value
                prompt = ChatPromptTemplate.from_template(selected_template.template)
                formatted_messages = prompt.format_messages(**input_values)
                formatted_message = formatted_messages[0].content                    
                chat_wrapper = HuggingChatWrapper()
                chat_wrapper.switch_model(model_name)            
                query_result = chat_wrapper.chat(formatted_message, use_web_search)                
                display_query_result = True
                       
            if st.sidebar.button("Delete all Chats on Server"):
                chat_wrapper.delete_all()
                st.success("All Chats on Server deleted!")           
                    
            if display_query_result:
                st.text_area(label="Prompt", value=formatted_messages,height=500, max_chars=None)
                st.text_area(label="LLM Response",value=query_result,height=500)                
                for source in query_result.web_search_sources:
                    st.markdown(source.title + ": " + source.link)
            
            if not keep_chat_on_server:
                chat_wrapper.reset()

if __name__ == "__main__":
    main()