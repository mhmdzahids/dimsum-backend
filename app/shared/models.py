from datetime import datetime

class SerializableMixin:
    def to_dict(self, exclude=None):
        exclude = exclude or set()
        result = {}
        for col in self.__table__.columns:
            if col.name not in exclude:
                val = getattr(self, col.name)
                if isinstance(val, datetime):
                    val = val.isoformat() + 'Z'
                result[col.name] = val
        return result
