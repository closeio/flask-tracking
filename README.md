flask-tracking
==============

flask-tracking is a tracking app for Flask that logs HTTP request and response information in a capped MongoDB collection. For each request, the execution time is stored, making it easy to identify slow requests. flask-tracking supports [Flask-Login](http://packages.python.org/Flask-Login/) to store the currently logged in user and requires [MongoEngine](http://mongoengine.org/) to store the tracking information.

## Installation

In your main application file, install the tracking app as follows:

```
from flask_tracking import Tracking
Tracking(app)
```

Make sure to set up the tracking app as early as possible to ensure accurate logging of the response and execution time. If you're using [Flask-gzip](https://github.com/closeio/Flask-gzip), install the tracking middleware afterwards to avoid logging compressed responses.

From now on, all requests are stored in the tracking collection.

## Configuration

- `TRACKING_EXCLUDE`: A list of regular expressions of paths that you want to exclude from being tracked.

    Example:
```
TRACKING_EXCLUDE = [
    '^/favicon.ico$',
    '^/static/',
    '^/_debug_toolbar/',
]
```

- `TRACKING_EXCLUDE_BODY`: A list of regular expressions of paths where you don't want to track the request and response body. This is useful if specific paths receive or return sensitive data.

    Example:
```
TRACKING_EXCLUDE_BODY = [
    '^/auth/login/$'
]
```

- `TRACKING_MAX_BODY_LENGTH`: The maximum size in bytes of the request and response body that should be stored.

## Examples

The following query shows all requests that took longer than one second to execute.

```
from flask_tracking.documents import Tracking
Tracking.objects.filter(execution_time__gte=1000)
```

The following query shows all requests that were served between 23:40 and 23:45 UTC on October 22th, 2012:

```
from flask_tracking.documents import Tracking
Tracking.objects.filter(date_created__gte='2012-10-22 23:40:00', date_created__lte='2012-10-22 23:45:00')
```

## Storing custom data

Sometimes it is useful to store custom data in the tracking table for a given request. To do that, simply assign your data to `request._tracking_data`. Example:

```
from flask import request
def my_view():
    request._tracking_data = {'action: 'view', 'my_stuff': [1, 2, 3]}
    return render()
```

Custom data is stored in a `DynamicField` called `custom_data` and can therefore contain any information.
