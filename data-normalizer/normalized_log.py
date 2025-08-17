class NormalizedLog:
    def __init__(self, siem_metadata, parsed_data):
        self.timestamp = parsed_data.pop("timestamp")
        self.siem_metadata = siem_metadata    
        self.parsed_data = parsed_data

    def to_dict(self):
        norm_log = {
            "@timestamp": self.timestamp,
            "siem_metadata": self.siem_metadata,
            **self.parsed_data
        }
        return norm_log