from .cybersecurity import Cybersecurity
from .finance import FinancialServices
from .healthcare import Healthcare
from .transportation import Transportation

SECTORS = {
    "cybersecurity": Cybersecurity(),
    "financial_services": FinancialServices(),
    "healthcare": Healthcare(),
    "transportation": Transportation(),
}

def get_sector(key: str):
    return SECTORS.get(key)
