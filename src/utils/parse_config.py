import yaml

IS_DEBUG = True

# Load the YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Function to replace placeholders in the config
def replace_placeholders(config):
    for key, value in config.items():
        if isinstance(value, str):
            # Replace placeholders with actual values from the config
            config[key] = value.replace('${OLD_VERSION}', config.get('OLD_VERSION', ''))
            config[key] = config[key].replace('${VERSION}', config.get('VERSION', ''))
    return config

# Replace placeholders
config = replace_placeholders(config)

if IS_DEBUG:
    print("\nConfig:")
    print(config)
    print("\n")