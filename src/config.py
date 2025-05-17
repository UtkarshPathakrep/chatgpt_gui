import json
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


mysql_config_json = json.load(open("C:\\utkarsh\\personal\\gui_openai_project\\config\\mysql_connector.json"))


MYSQL_CONFIG = {
    'host': mysql_config_json.get("mysql").get("host"),
    'user': mysql_config_json.get("mysql").get("user"),
    'password': mysql_config_json.get("mysql").get("password"),
    'database': mysql_config_json.get("mysql").get("database")
}