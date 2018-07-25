class NotValidModuleException(Exception):
    def __init__(self, reason, additional=""):
        super().__init__(reason)
        self.reason = reason
        self.additional = additional