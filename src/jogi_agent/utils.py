import configparser
from datetime import datetime
from pathlib import Path
from crewai import Agent, Task
import yaml

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

def init_deep_analysis(is_verbose: bool):
    BASE_DIR = Path(__file__).resolve().parent

    with open(BASE_DIR / "config" / "deep_analyst_agent.yaml", "r", encoding='UTF-8') as f:
        agents_config = yaml.safe_load(f)

    with open(BASE_DIR / "config" / "deep_analysis_task.yaml", "r", encoding='UTF-8') as f:
        tasks_config = yaml.safe_load(f)

    da_agent = Agent(
        config=agents_config["deep_analyst"],
        verbose=is_verbose
    )

    return tasks_config, da_agent

def run_deep_analysis(tasks_config, question: str, formatted_history: str, da_agent: Agent):
    # format: topic, history
    tasks_config["deep_analysis_feladat"]["description"] = tasks_config["deep_analysis_feladat"][
        "description"].format(
        topic=question,
        history=formatted_history
    )

    da_task = Task(
        config=tasks_config["deep_analysis_feladat"],
        agent=da_agent
    )

    # run deep analysis
    return str(da_task.execute_sync())



