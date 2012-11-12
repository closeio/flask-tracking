from mongoengine import *

class UserAgent(EmbeddedDocument):
    browser = StringField()
    language = StringField()
    platform = StringField()
    string = StringField()
    version = StringField()

class Tracking(Document):
    #session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    date_created = DateTimeField()
    host = StringField()
    path = StringField()
    query_params = StringField()
    ip = StringField()
    user = GenericReferenceField()
    user_agent = EmbeddedDocumentField(UserAgent)

    method = StringField()
    request_headers = ListField()
    request_body = BinaryField()

    status_code = IntField()
    response_headers = ListField()
    response_body = BinaryField()

    # Execution time in ms
    execution_time = IntField()

    custom_data = DynamicField()

    meta = {
        'max_documents': 10**6, # 1 million
        'indexes': ['date_created'],
        'ordering': ['-date_created'],
    }
