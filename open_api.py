import openai
import os

openai.api_key = os.getenv("OPENAI_API")


def generate_system_message() -> str:
    return """
    You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database.
    Provide a set of Nodes in the form [ENTITY_ID, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES].
    It is important that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID. If you can't pair a relationship with a pair of nodes don't add it.
    When you find a node or relationship you want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a label.

    Example:
    Data: Alice lawyer and is 25 years old and Bob is her roommate since 2001. Bob works as a journalist. Alice owns a the webpage www.alice.com and Bob owns the webpage www.bob.com.
    Nodes: ["alice", "Person", {"age": 25, "occupation": "lawyer", "name":"Alice"}], ["bob", "Person", {"occupation": "journalist", "name": "Bob"}], ["alice.com", "Webpage", {"url": "www.alice.com"}], ["bob.com", "Webpage", {"url": "www.bob.com"}]
    Relationships: ["alice", "roommate", "bob", {"start": 2021}], ["alice", "owns", "alice.com", {}], ["bob", "owns", "bob.com", {}]
    """


def generate_prompt(data) -> str:
    return f"""
    Data: {data}"""


def request_open_api(doc):
    system_message = generate_system_message()
    prompt_string = generate_prompt(doc)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt_string},
    ]

    # Using open AI to extract nodes from article
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    output_str = [output.to_dict().get('choices')[0].get("message").to_dict().get("content")]

    return output_str

