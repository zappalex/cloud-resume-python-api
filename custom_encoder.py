import json
from decimal import Decimal
class CustomEncoder(json.JSONENCODER):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        return json.JSONENCODER.default(self, obj)