import configparser
from datetime import datetime
from pathlib import Path

import jsonschema
import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore

def get_config():
    config = configparser.ConfigParser()
    current_dir = Path(__file__).parent

    config_path = current_dir / 'config/config.ini'
    read_files = config.read(config_path)

    if not read_files:
        raise Exception(f"Config is not found at the location of {config_path}")
    else:
        is_verbose = config.getboolean('crewai', 'VERBOSE_ENABLED')
        is_deep_analysis_enabled = config.getboolean('crewai', 'DEEP_ANALYSIS_ENABLED')
        return {
            "is_verbose": is_verbose,
            "is_deep_analysis_enabled": is_deep_analysis_enabled
        }

def initialize_firebase():
    firebase_credentials_base64= os.environ['FIREBASE_CREDENTIALS_BASE64']

    creditials_json = base64.b64decode(firebase_credentials_base64).decode('utf-8')

    credentials_dict = json.loads(creditials_json)
    cred = credentials.Certificate(credentials_dict)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    return firestore.client()

def format_history_for_prompt(history: list[dict[str, str]], max_turns: int = 5) -> str:
    if not history:
        return "Nincs korábbi előzmény."

    recent_history = history[-max_turns * 2:]

    formatted_turns = []
    for turn in recent_history:
        role = turn["role"]
        content = turn["content"].strip()
        formatted_turns.append(f"### {role}:\n{content}")

    return "\n\n".join(formatted_turns)




