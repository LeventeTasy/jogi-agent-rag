import configparser

def create_config():
    config = configparser.ConfigParser()
    # Add sections and key-value pairs
    config['crewai'] = {
        'VERBOSE_ENABLED': 'True',
        'HISTORY_ENABLED': 'False'
    }

    with open('jogi_agent/config/config.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    create_config()



