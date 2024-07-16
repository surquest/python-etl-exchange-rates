import os
from surquest.utils.loader import Loader

from utils.misc import create_enum_class

currencies = [
    pair.get("code") for pair in Loader.load_json(
        f"{os.getenv('PROJECT_DIR')}/config/subjects/fx.currencies.json"
    ).get("currencies")
]

Currencies = create_enum_class(
    enum_list=currencies,
    name="Currencies"
)

