from webargs import fields
from flask_restful_swagger import swagger


@swagger.model
class NewsModelSchema:
    title = fields.Str(required=True , default='News title')
    articlBody = fields.Str(default='News body')
    pubDate = fields.Int(required=True , default=1111111111)
    keywords = fields.List(fields.Str())
    author = fields.Str(default='News author')
    link = fields.Str(required=True , default ='news URL')
    provider = fields.Str(required=True , default = 'news source')
    summary = fields.Str(default = 'brief summary')
    sentiment = fields.Str(default = 'positive')
    SentimentScore = fields.List(fields.Int())
    thImage = fields.Str(default = 'image url')
    images = fields.Str(default = 'List of Images')
