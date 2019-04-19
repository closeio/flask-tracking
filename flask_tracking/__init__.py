import datetime
import re
import socket
import time

import mongoengine
import pymongo
from bson.errors import InvalidStringData
from flask import request
from flask.ext.tracking import documents
from flask.ext.tracking.utils import WSGICopyBody
from mongoengine import Document

try:
    from flask.ext.login import current_user
except ImportError:
    current_user = None

class Tracking(object):
    def __init__(self, app, user_repr=None):
        app.before_request(self.track_before)
        app.after_request(self.track_after)
        app.wsgi_app = WSGICopyBody(app.wsgi_app)

        self.hostname = socket.gethostname()

        self.max_body_length = app.config.get('TRACKING_MAX_BODY_LENGTH', 64*1024)
        self.exclude_paths = app.config.get('TRACKING_EXCLUDE', [])
        self.exclude_methods = app.config.get('TRACKING_EXCLUDE_METHODS', [])
        self.exclude_body_paths = app.config.get('TRACKING_EXCLUDE_BODY', [])
        self.exclude_status_codes = app.config.get('TRACKING_EXCLUDE_STATUS_CODES', [])
        self.min_execution_time = app.config.get('TRACKING_MIN_EXECUTION_TIME', 0)
        self.table_size = app.config.get('TRACKING_TABLE_SIZE', 100*1024*1024)

        documents.Tracking._meta['max_size'] = self.table_size
        if user_repr:
            documents.Tracking.user_repr = user_repr

    def track_before(self):
        request._start_time = time.time()

    def track_after(self, response):
        can_process = True

        if request.method in self.exclude_methods:
            can_process = False

        for path in self.exclude_paths:
            if re.match(path, request.path):
                can_process = False
                break

        can_store_body = True

        for path in self.exclude_body_paths:
            if re.match(path, request.path):
                can_store_body = False
                break

        if getattr(request, '_start_time', None):
            execution_time = int((time.time() - request._start_time) * 1000)
        else:
            execution_time = None

        # process the request if its status is not excluded or if its
        # execution time was higher than the min threshold
        if response.status_code in self.exclude_status_codes and (execution_time is None or execution_time < self.min_execution_time):
            can_process = False

        if can_process:
            try:
                user = current_user._get_current_object()
                if not isinstance(user, Document):
                    user = None
            except AttributeError:
                user = None

            now = datetime.datetime.utcnow()

            ua = request.user_agent

            t = documents.Tracking(
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
                request_body=can_store_body and request.environ.get('body_copy','')[:self.max_body_length] or '',
                request_headers=request.headers.items(),
                status_code=response.status_code,
                response_headers=response.headers.to_wsgi_list(),
                response_body=can_store_body and response.data[:self.max_body_length] or '',
                execution_time=execution_time,
                custom_data=getattr(request, '_tracking_data', None),
                hostname=self.hostname,
            )
            try:
                t.save(cascade=False, write_concern={'w': -1, 'fsync': False})
            except (mongoengine.connection.ConnectionError, pymongo.errors.AutoReconnect, InvalidStringData):  # InvalidStringData is raised when a BSON object can't be encoded
                pass

        return response
