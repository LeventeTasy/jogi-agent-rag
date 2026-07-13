import configparser
from pathlib import Path

def get_config():
    config = configparser.ConfigParser()
    current_dir = Path(__file__).parent

    config_path = current_dir / 'config/config.ini'
    read_files = config.read(config_path)

    if not read_files:
        raise Exception(f"Config is not found at the location of {config_path}")
    else:
        is_verbose = config.getboolean('crewai', 'VERBOSE_ENABLED')
        is_memory = config.getboolean('crewai', 'HISTORY_ENABLED')
        is_deep_analysis_enabled = config.getboolean('crewai', 'DEEP_ANALYSIS_ENABLED')
        return {
            "is_verbose": is_verbose,
            "is_memory": is_memory,
            "is_deep_analysis_enabled": is_deep_analysis_enabled
        }