class Manga:
    def __init__(self, id, languange_name):
        self.id = id
        self.languange_name = languange_name

    def to_dict(self):
        return {
            "id": self.id,
            "language": self.language,
        }