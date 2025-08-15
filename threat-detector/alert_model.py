class Alert:
    def __init__(self, confidence, log_data):
        self.confidence = confidence
        self.log_data = log_data

    def to_dict(self):
        return {
            "confidence": self.confidence,
            "log_data": self.log_data
        }