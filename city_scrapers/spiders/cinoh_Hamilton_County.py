from city_scrapers.mixins.cinoh_Hamilton_County import CinohHamiltonCountyMixin

spider_configs = [
    {
        "class_name": "CinohHamiltonCommissionSpider",
        "name": "cinoh_hamilton_commission",
        "agency": "Hamilton County Commission Meetings",
        "agency_name": "Hamilton County Board of County Commissioners",
        "categories": [
            "Commission Meetings",
            "Public Hearings",
            "BoCC Holidays",
            "Community Event",
        ],
    },
    {
        "class_name": "CinohHamiltonBoardsCommissionsSpider",
        "name": "cinoh_hamilton_boards_commissions",
        "agency": "Hamilton County Boards & Commissions",
        "agency_name": "Hamilton County Board of County Commissioners",
        "categories": ["Boards & Commissions"],
    },
]


def create_spiders():
    """
    Dynamically create spider classes using the spider_configs list
    and register them in the global namespace.
    """
    for config in spider_configs:
        class_name = config["class_name"]

        if class_name not in globals():
            # Build attributes dict without class_name to avoid duplication.
            # We make sure that the class_name is not already in the global namespace
            # Because some scrapy CLI commands like `scrapy list` will inadvertently
            # declare the spider class more than once otherwise
            attrs = {k: v for k, v in config.items() if k != "class_name"}

            # Dynamically create the spider class
            spider_class = type(
                class_name,
                (CinohHamiltonCountyMixin,),
                attrs,
            )

            # Register the class in the global namespace using its class_name
            globals()[class_name] = spider_class


# Create all spider classes at module load
create_spiders()
