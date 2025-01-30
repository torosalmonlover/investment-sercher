import os
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load JSON template
with open("backend/llm_interface_conf.json", "r") as file:
    config_data = json.load(file)

# Replace placeholders with actual environment values
def replace_env_vars(obj):
    if isinstance(obj, dict):
        return {key: replace_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("$"):
        return os.getenv(obj[1:], obj)  # Remove "$" and fetch env value
    return obj

# Process the JSON
config_data = replace_env_vars(config_data)

# Save the final JSON with real values (optional)
with open("config.json", "w") as file:
    json.dump(config_data, file, indent=4)

# Print the processed config
print(json.dumps(config_data, indent=4))
