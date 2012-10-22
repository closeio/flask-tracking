import datetime
import re
import time

from flask import request, current_app
from flask.ext.tracking import documents
from flask.ext.tracking.utils import WSGICopyBody

from mongoengine import Document

try:
    from flask.ext.login import current_user
except ImportError:
    current_user = None

class Tracking(object):
    def __init__(self, app):
        app.before_request(self.track_before)
        app.after_request(self.track_after)
        app.wsgi_app = WSGICopyBody(app.wsgi_app)

        self.max_body_length = app.config.get('TRACKING_MAX_BODY_LENGTH', 64*1024)
        self.exclude_paths = app.config.get('TRACKING_EXCLUDE', [])
        self.exclude_body_paths = app.config.get('TRACKING_EXCLUDE_BODY', [])

    def track_before(self):
        request._start_time = time.time()

    def track_after(self, response):
        can_process = True

        for path in self.exclude_paths:
            if re.match(path, request.path):
                can_process = False
                break

        can_store_body = True

        for path in self.exclude_body_paths:
            if re.match(path, request.path):
                can_store_body = False
                break

        if can_process:
            user = current_user._get_current_object()
            if not isinstance(user, Document):
                user = None

            now = datetime.datetime.utcnow()

            ua = request.user_agent

            documents.Tracking.objects.create(
                date_created=now,
                host=request.host,
                path=request.path,
                query_params=request.query_string,
                method=request.method,
                user=user,
                user_agent=documents.UserAgent(
                        browser=ua.browser,
                        language=ua.language,
                        platform=ua.platform,
                        string=ua.string,
                        version=ua.version,
                    ),
                request_body=can_store_body and request.environ['body_copy'][:self.max_body_length] or '',
                request_headers=request.headers.items(),
                status_code=response.status_code,
                response_headers=response.header_list,
                response_body=can_store_body and response.data[:self.max_body_length] or '',
                execution_time=time.time() - request._start_time,
            )

        return response
