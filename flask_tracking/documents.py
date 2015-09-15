from mongoengine import *
import json

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

    # System hostname
    hostname = StringField()

    custom_data = DynamicField()

    meta = {
        'max_documents': 10**6, # 1 million
    }

    def user_repr(self):
        if self._data['user']:
            if isinstance(self._data['user'], dict):
                return self._data['user']['_ref'].id
            else:
                return self.user.id
        else:
            return '-'

    def __unicode__(self):
        return '{id} {date} {method} {user} {path}{query} {status} ({time} ms)'.format(
            id=self.id,
            date=self.date_created.strftime('%Y-%m-%d %H:%M:%S.%f'),
            method=self.method,
            user=self.user_repr(),
            path=self.path,
            query=self.query_params and '?%s' % self.query_params or '',
            status=self.status_code,
            time=self.execution_time)

    def debug(self):
        ret = '%s %s%s%s\n' % (self.method, self.host, self.path, self.query_params and '?%s' % self.query_params or '')
        ret += 'REQUEST:\n'
        ret += self.format_headers(self.request_headers) + '\n'
        ret += self.format_body(self.request_body) + '\n'
        ret += '%s RESPONSE:\n' % self.status_code
        ret += self.format_headers(self.response_headers) + '\n'
        ret += self.format_body(self.response_body)
        return ret

    def get_header(self, name, default=''):
        return { h[0]: h[1] for h in self.request_headers }.get(name, default)

    def replay(self):
        from flask import current_app

        client = current_app.test_client()

        # Make sure we don't send invalid cookies.
        client.cookie_jar.clear()

        full_path = self.path + ('?'+self.query_params if self.query_params else '')

        method_func = getattr(client, self.method.lower())

        return method_func(
            full_path,
            headers=self.request_headers,
            data=self.request_body,
            content_type=dict(self.request_headers)['Content-Type']
        )

    @staticmethod
    def format_body(inpt):
        """Format an HTTP body as JSON if possible, otherwise return string"""
        try:
            return json.dumps(json.loads(inpt.decode('utf8')), indent=4)
        except ValueError:
            return repr(inpt)

    @staticmethod
    def format_headers(headers):
        return '\n'.join(['  %s: %s' % (h[0], h[1] if len(h[1]) < 100 else '%s...' % h[1][:100]) for h in headers])
