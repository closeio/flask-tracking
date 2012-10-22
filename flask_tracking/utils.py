# From http://stackoverflow.com/questions/10999990/python-flask-how-to-get-whole-raw-post-body
class WSGICopyBody(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):

        from cStringIO import StringIO
        length = environ.get('CONTENT_LENGTH', '0')
        length = 0 if length == '' else int(length)

        body = environ['wsgi.input'].read(length)
        environ['body_copy'] = body
        environ['wsgi.input'] = StringIO(body)

        # Call the wrapped application
        app_iter = self.application(environ,
                                    self._sr_callback(start_response))

        # Return modified response
        return app_iter

    def _sr_callback(self, start_response):
        def callback(status, headers, exc_info=None):

            # Call upstream start_response
            start_response(status, headers, exc_info)
        return callback

