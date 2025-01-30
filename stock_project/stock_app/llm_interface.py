from openai import OpenAI
import json

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def chatgpt_interface(config_file='backend/llm_interface_conf.json', system_role='You are a useful assistant.', user=''):
    """
    Interface to interact with ChatGPT using OpenAI API.

    Args:
        config_file (str): Path to the configuration JSON file.
        system_role (str): Role of the system in the conversation.
        user (str): User input for the conversation.

    Returns:
        str: Response from ChatGPT.
    """
    # Load configuration
    config = load_config(config_file)

    # Extract API configuration
    api_key     = config['llm_interface_conf']['chatgpt_interface']['api_key']
    model       = config['llm_interface_conf']['chatgpt_interface']['model']
    max_tokens  = config['llm_interface_conf']['chatgpt_interface']['max_tokens']
    temperature = config['llm_interface_conf']['chatgpt_interface']['temperature']

    # Generate the message
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user}
    ]

    # Create the OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Generate the response from ChatGPT
    response = client.chat.completions.create(
        model=model, 
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages
    )
    
    # Extract the response text from ChatGPT
    response_text = response.choices[0].message.content

    return response_text