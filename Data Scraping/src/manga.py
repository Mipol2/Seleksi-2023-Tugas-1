class Manga:
    def __init__(self, id, title, author, language):
        self.id = id
        self.title = title
        self.author = author
        self.language = language
        self.description = None
        
    def setDescription(self, description):
        self.description = description
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'language': self.language
        }
