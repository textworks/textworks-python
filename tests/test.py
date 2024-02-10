import textworks
import json
import os

if __name__ == '__main__':
    # Set the environment variable to the local server
    os.environ[textworks.ENV_VAR_TEXTWORKS_URL] = "http://localhost:3000/api/"

    # Usage example
    logger = textworks.TextworksLogger(
        # example run ID
        "37c0486d-3d68-488a-8e06-e7cac6a415f3",
        # example API key
        "5f1f4f157ba7e6c7800dff3978f8b2c007d1bd332e306e86265cec95db5aaa78",
    )
    if not logger.health_check():
        raise ValueError("oh no!")
    
    print("API is healthy!")

    data = {"temperature": 22, "humidity": 67}
    logger.log(data, commit=True)

    data = {"temperature": 23, "humidity": 68}
    logger.log(data, commit=True)

    print(json.dumps(logger.get_logs(), indent=4))
