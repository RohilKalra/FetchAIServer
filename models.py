from uagents import Model

class Request(Model):
    text: str

class Response(Model):
    text: str

class Error(Model):
    text: str

class Data(Model):
    value: str
    unit: str
    timestamp: str
    confidence: float
    source: str
    notes: str
