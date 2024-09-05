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


def create_input_fields(template):
    """
    Create Streamlit input fields for string variables.

    Args:
        template (str): The prompt template containing input variables.

    Returns:
        dict: A dictionary with variable names as keys and their corresponding
              Streamlit input values.
    """
    prompt_template = ChatPromptTemplate.from_template(template)

    variables = prompt_template.messages[0].prompt.input_variables
    inputs = {}
    for variable in variables:
        var_name = variable
        if len(variables) > 1:
            inputs[var_name] = st.text_input(var_name)
        else:
            inputs[var_name] = st.text_area(var_name, height=200)
    return inputs


def get_template_names(template_use=False):
    """
    Retrieve templates by topic from the database.

    Returns:
        list: A list of prompt templates filtered by the selected topic.
    """
    topics = PromptTemplate.get_topics(session)
    selected_topic = st.sidebar.selectbox(
        "Select Topic", ["All"] + topics
    )  # Add dropdown for selecting topic
    if selected_topic == "All":
        templates = PromptTemplate.get_all_templates(session)
    else:
        templates = PromptTemplate.get_templates_by_topic(session, selected_topic)

    if not template_use:
        template_names = ["New Template"]  # Make "New Template" the first option
        template_names.extend([template.name for template in templates])
    else:
        template_names = [template.name for template in templates]

    return template_names


def main():
    """
    Main function to run the Streamlit app.

    Initializes the session state and displays the sidebar and main content based on user actions.
    """

    initialize_session_state()

    st.sidebar.title("Select Action")

    action = st.sidebar.radio(
        "Action", ["Edit Template", "Use Template", "Prompting Principles"]
    )

    if action == "Prompting Principles":
        st.markdown(prompting_principles)

    if action == "Edit Template":
        st.sidebar.title("Select Prompt Template")
        template_names = get_template_names()
        selected_template_name = get_selected_template_name(template_names)

        if selected_template_name == "New Template":
            create_template(template_names)
        else:
            maintain_template(template_names, selected_template_name)

    elif action == "Use Template":
        use_template()


def get_selected_template_name(template_names):
    """
    Get the name of the selected template.

    Parameters:
    - template_names (list): A list of strings representing the names of available templates.

    Returns:
    - str: The name of the selected template.
    """
    selected_template_name = st.sidebar.selectbox("Template", template_names)
    return selected_template_name


def initialize_session_state():
    """
    Initialize the session state with empty model names if not already set.
    """
    if "model_names" not in st.session_state:
        st.session_state["model_names"] = []
        
    if 'hf_email' not in st.session_state:
        st.session_state["hf_email"] = ''
        
    if 'hf_pwd' not in st.session_state:
        st.session_state["hf_pwd"] = ''


def use_template():
    """
    Handle the use of a selected prompt template to interact with the LLM.

    Displays the template, collects input variables, sends the formatted prompt to the LLM, and shows the response.
    """
    st.sidebar.title("Select Prompt Template")
    template_names = get_template_names(template_use=True)

    selected_template_name = st.sidebar.selectbox("Template", template_names)

    selected_template = PromptTemplate.get_by_name(session, selected_template_name)

    if selected_template:
        display_template(selected_template)

        model_names = get_model_names()

        # Display available models in selectbox
        model_name = st.sidebar.selectbox("Select Model", model_names)

        inputs = create_input_fields(selected_template.template)
       
        side_col1, side_col2 = st.sidebar.columns(2)
        use_web_search = side_col1.checkbox( "Use Web Search", selected_template.use_web_search )

        keep_chat_on_server = side_col2.checkbox("Keep chat on Server")

        
        if st.button("Submit"):
            formatted_message = get_formatted_message(selected_template, inputs)
            chat_wrapper, query_result = call_llm(
                model_name, use_web_search, formatted_message
            )
                
            st.text_area(
                label="Prompt", value=formatted_message, height=500, max_chars=None
            )                        
            st.markdown("LLM Response")
            st.markdown(query_result)
            conversations = chat_wrapper.chatbot.get_conversation_list()

            for conversation in conversations:                
                st.markdown(conversation.id + ' ' + conversation.model + ' ' + conversation.title)
                for message in conversation.history:
                    st.markdown(message.id + ' ' + message.role)

            if use_web_search:
                for source in query_result.web_search_sources:
                    st.markdown(source.title + ": " + source.link)

            if not keep_chat_on_server:
                chat_wrapper.reset()
        
        
                
        hf_email = st.sidebar.text_input(label='HuggingFace E-Mail')
        if hf_email:
            st.session_state['hf_email'] = hf_email
        
        hf_pwd = st.sidebar.text_input(label='HuggingFace Password')
        if hf_pwd:
            st.session_state['hf_pwd'] = hf_pwd
                        
        
        if st.sidebar.button("Delete all Chats on Server"):
            chat_wrapper = HuggingChatWrapper()
            chat_wrapper.delete_all()
            st.success("All Chats on Server deleted!")


def display_template(selected_template):
    """
    Display the selected template's details.

    Args:
        selected_template (PromptTemplate): The selected prompt template.
    """
    st.write(f"Topic: {selected_template.topic}")
    st.write(f"Name: {selected_template.name}")
    st.write(f"Purpose: {selected_template.purpose}")
    st.write(f"Template: {selected_template.template}")


def call_llm(model_name, use_web_search, formatted_message):
    """
    Call the LLM with the formatted message.

    Args:
        model_name (str): The name of the model to use.
        use_web_search (bool): Whether to use web search.
        formatted_message (str): The formatted message to send to the LLM.

    Returns:
        tuple: A tuple containing the chat wrapper instance and the query result.
    """
    chat_wrapper = HuggingChatWrapper()
    chat_wrapper.switch_model(model_name)
    query_result = chat_wrapper.chat(formatted_message, use_web_search)
    return chat_wrapper, query_result


def get_formatted_message(selected_template, inputs):
    """
    Format the message based on the selected template and input values.

    Args:
        selected_template (PromptTemplate): The selected prompt template.
        inputs (dict): The dictionary of input values.

    Returns:
        str: The formatted message.
    """
    input_values = {}
    for var_name, var_value in inputs.items():
        input_values[var_name] = var_value
    prompt = ChatPromptTemplate.from_template(selected_template.template)
    formatted_messages = prompt.format_messages(**input_values)
    formatted_message = formatted_messages[0].content
    return formatted_message


def get_model_names():
    """
    Get the list of available model names.

    Returns:
        list: A list of available model names.
    """
    if st.session_state["model_names"] == []:
        try:
            chat_wrapper = HuggingChatWrapper()
            model_names = chat_wrapper.get_available_models()
            st.session_state["model_names"].append(model_names)
            chat_wrapper.reset()
        except Exception as e:
            st.error(e)
    else:
        model_names = st.session_state["model_names"][0]

    return model_names


def maintain_template(template_names, selected_template_name):
    """
    Maintain the selected template, providing options to update or delete it.

    Args:
        template_names (list): A list of all template names.
        selected_template_name (str): The name of the selected template.
    """
    selected_template = PromptTemplate.get_by_name(session, selected_template_name)
    if selected_template:
        topic, name, purpose, use_web_search, template = get_template_values(
            selected_template
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key="save_button"):
                update_template(
                    template_names,
                    selected_template_name,
                    selected_template,
                    topic,
                    name,
                    purpose,
                    use_web_search,
                    template,
                )
        with col2:
            delete_template(selected_template)


def get_template_values(selected_template):
    """
    Get the values of the selected template's fields.

    Args:
        selected_template (PromptTemplate): The selected prompt template.

    Returns:
        tuple: A tuple containing the topic, name, purpose, use_web_search, and template content.
    """
    topic = st.text_input("Topic", value=selected_template.topic)
    name = st.text_input("Name", value=selected_template.name)
    purpose = st.text_area("Purpose", value=selected_template.purpose)
    use_web_search = st.checkbox(
        "Use Web Search", value=selected_template.use_web_search
    )
    template = st.text_area("Template", value=selected_template.template, height=400)
    return topic, name, purpose, use_web_search, template


def update_template(
    template_names,
    selected_template_name,
    selected_template,
    topic,
    name,
    purpose,
    use_web_search,
    template,
):
    """
    Update the selected template with new values.

    Args:
        template_names (list): A list of all template names.
        selected_template_name (str): The name of the selected template.
        selected_template (PromptTemplate): The selected prompt template instance.
        topic (str): The updated topic.
        name (str): The updated name.
        purpose (str): The updated purpose.
        use_web_search (bool): The updated web search usage flag.
        template (str): The updated template content.
    """
    if not topic:
        st.error("Please enter a topic for the template!")
    if not name:
        st.error("Please enter a name for the template!")
    else:
        if name != selected_template_name and name in template_names[1:]:
            st.error("A template with this name already exists!")
        else:
            selected_template.name = name
            selected_template.purpose = purpose
            selected_template.use_web_search = use_web_search
            selected_template.template = template
            session.commit()
            st.success("Changes saved successfully!")


def delete_template(selected_template):
    """
    Delete the selected template from the database.

    Args:
        selected_template (PromptTemplate): The selected prompt template to be deleted.
    """
    if st.button("Delete", key="delete_button") and selected_template:
        session.delete(selected_template)
        session.commit()
        st.success("Template deleted successfully!")


def create_template(template_names):
    """
    Create a new template based on user input.

    Args:
        template_names (list): A list of existing template names.
    """
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
                    use_web_search=use_web_search,
                )
                session.add(new_template)
                session.commit()
                st.success("Template saved successfully!")


if __name__ == "__main__":
    main()
