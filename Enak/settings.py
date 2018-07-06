import configparser


class Config:
    def __init__(self, path="./sub/settings.ini"):
        self.config = configparser.ConfigParser()
        self.path = path

        self._load_config(path)

    def _load_config(self, path):
        self.config.read(path)

    def get(self, ind: str):
        if not ind: raise Exception("Invalid setting path passed")

        ind = ind.split(".", 1)

        if len(ind) > 1:
            grp, key = ind
            return self.config.get(grp, key)
        else:
            grp,  = ind
            return dict([(k, v) for k,v in self.config[grp].items()])
