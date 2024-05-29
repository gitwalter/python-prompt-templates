import pandas as pd
from prompt_template_database import session, PromptTemplate
def import_csv_to_db(csv_file):
    # Read the CSV file
    data = pd.read_csv(csv_file)

    # Iterate over each row and add to the database
    for index, row in data.iterrows():
        topic = "Role Prompts"
        name = row['act']
        template = row['prompt']
        purpose = "Tells the model to act as " + row['act']

        # Create and add the PromptTemplate instance to the session
        prompt_template = PromptTemplate(topic=topic, name=name, purpose=purpose, template=template)
        session.add(prompt_template)

    # Commit the session to save changes to the database
    session.commit()

    # Close the session
    session.close()

if __name__ == "__main__":
    csv_file_path = 'prompts.csv'
    import_csv_to_db(csv_file_path)
