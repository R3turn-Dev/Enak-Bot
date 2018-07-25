from configparser import RawConfigParser


class Config:
    def __init__(self, path="./sub/settings.ini"):
        self.config = RawConfigParser()
        self.file = path

        self._read(path)

    def _read(self, path):
        self.config.read(path)

    def _get(self, option: str):
        options = option.split(".", 1)

        if len(options) == 1:
            ret = {}
            for k, v in self.config._proxies[option].items():
                if v.isnumeric():
                    ret[k] = int(v)
                elif v.lower() in ["true", "false"]:
                    ret[k] = bool(v)
                else:
                    ret[k] = v

            return ret

        if len(options) == 2:
            return self.config.get(options[0], options[1])

    def get(self, option: str):
        return self._get(option)