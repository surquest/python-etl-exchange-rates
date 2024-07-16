import json
from surquest.utils.config.formatter import Formatter
from surquest.GCP.bq.grid import Grid

def define_env(env):


    conf_vars = dict() # dictionary of variables to be used in markdown pages
    config_files = {
        "solution": "../config/config.solution.json",
        "services": "../config/config.cloud.google.services.json",
    }
    env_files = {
        "PROD": "../config/config.cloud.google.env.PROD.json",
    }

    formatter = Formatter(
        config=Formatter.import_config(
            configs={
                "GCP": env_files.get("PROD"),
                "services": config_files.get("services"),
                "solution": config_files.get("solution")
            }
        ),
        naming_patterns=Formatter.load_json(
            path="../config/naming.patterns.json",
        )
    )

    # load config files
    for key, file in config_files.items():
        with open(file) as f:
            conf_vars[key] = json.load(f).get(key)

    # load env files
    conf_vars["env"] = dict()
    for key, file in env_files.items():
        with open(file) as f:
            conf_vars["env"][key] = json.load(f).get("GCP")


    # add to the dictionary of variables available to markdown pages:
    env.variables["conf"] = conf_vars

    def get_grid_schema(path):

        table = Grid._load_yaml(path=path)


        return Grid.get_markdown_table(
            schema = table.get("schema"),
        )

        # If you wish, you can  declare a macro with a different name:

    env.macro(formatter.get, 'pattern')
    env.macro(get_grid_schema, 'grid_schema')
