class Manga:
    def __init__(self, id, title, author, language, description):
        self.id = id
        self.title = title
        self.author = author
        self.language = language
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "description": self.description
        }