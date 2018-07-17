class RawParseError(Exception):
    def __init__(self, error, data=None):
        super().__init__(error)
        self.error = error
        self.data = data
