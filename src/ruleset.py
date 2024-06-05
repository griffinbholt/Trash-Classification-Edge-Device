from datetime import datetime
import json
import pycountry
from waste import WasteClass, WasteDestination

class Ruleset():
    """
    A ruleset mapping waste item to waste destination for a specified region.
    Meant to be easily interchangeable from region to region.
    """
    def __init__(self,
                 name: str,
                 date_updated: datetime,
                 country: pycountry.db.Country,
                 region: dict[str, str],
                 rules: dict[WasteClass, WasteDestination]):
        self.name = name
        self.date_updated = date_updated
        self.country = country
        self.region = region
        self.rules = rules

    def __call__(self, waste_class: WasteClass) -> WasteDestination:
        return self.rules[waste_class]

    def _to_dict(self) -> dict:
        return {
            "name": self.name,
            "date_updated": self.date_updated.isoformat(),
            "country": self.country.alpha_2,
            "region": self.region,
            "rules": {key.name: value.name for (key, value) in self.rules.items()}
        }

    def to_json(self, filename: str) -> str:
        with open(filename, "w") as file:
            json.dump(self._to_dict(), file, indent=4)

    @classmethod
    def _from_dict(self, dict_rep: dict):
        name = dict_rep["name"]
        date_updated = datetime.fromisoformat(dict_rep["date_updated"])
        country = pycountry.countries.get(alpha_2=dict_rep["country"])
        region = dict_rep["region"]
        rules = {WasteClass[key]: WasteDestination[value] for key, value in dict_rep["rules"].items()}
        return Ruleset(name, date_updated, country, region, rules)

    @classmethod
    def from_json(self, filename: str):
        with open(filename, "r") as file:
            ruleset = Ruleset._from_dict(json.load(file))
        return ruleset

"""
Demo Ruleset: saved to demo_ruleset.json
demo_ruleset = Ruleset(
    name="demo_ruleset",
    date_updated=datetime.now(),
    country=pycountry.countries.search_fuzzy('United States of America')[0],
    region={
        "state": "California",
        "county": "Santa Clara",
        "city": "Stanford"
    },
    rules={
        WasteClass.BATTERY: WasteDestination.ELECTRONICS_RECYCLING_CENTER,
        WasteClass.BIOLOGICAL: WasteDestination.COMPOST,
        WasteClass.CARDBOARD: WasteDestination.RECYCLE,
        WasteClass.CLOTHES: WasteDestination.LANDFILL,
        WasteClass.GLASS: WasteDestination.RECYCLE,
        WasteClass.METAL: WasteDestination.RECYCLE,
        WasteClass.PAPER: WasteDestination.RECYCLE,
        WasteClass.PLASTIC: WasteDestination.RECYCLE,
        WasteClass.SHOES: WasteDestination.LANDFILL,
        WasteClass.TRASH: WasteDestination.LANDFILL
    }
)
"""
