# Pellet

Pellet helps improve your Django app performance by discovering `N+1` queries.

The Django ORM makes it easy to forget using `select_related` and `prefetch_related` correctly and can accidentally cause `N+1` queries to happen.

Pellet ultimately aims to recreate [Bullet](https://github.com/flyerhzm/bullet) for Django.

## Installing Pellet

`pip install pellet`

## Enabling Pellet

1. Add `pellet.middleware.PelletMiddleware` to your django middleware list.
2. Configure pellet behaviour by using the `PELLET` variable in your django settings file.

## Configuring Pellet

You can configure pellet by setting the `PELLET` variable in your django settings file. The default values used by pellet if this variable or any field in the object is not found is as follows:

```python3
PELLET = {
    # Enable/Disable pellet
    # If set to False the pellet
    # middleware does nothing
    "enabled": False,

    # Enable this if you want count and time
    # metrics at a query level
    "query_level_metrics_enabled": False,

    # Settings related to response headers
    # set by pellet
    "headers": {

        # Enables setting response headers
        "enabled": False,

        # Header to be used for setting total query count
        "query_count_header": "X-Pellet-Count",

        # Header to be used for setting total query time
        "query_time_header": "X-Pellet-Time"
    },

    # Settings related to pellet debug mode
    "debug": {

        # Enable debug mode
        # Don't enable on prod as it will slow down your app
        "enabled": False,

        # Query count thresholds which will
        # be used by pellet to report metrics
        # on the console
        "count_threshold": {

            # Min number of times a query should happen
            # for it to be classified as N+1
            # Queries with less count than this will
            # not show up in the debug table
            "min": 2,

            # Max number of times a query should happen
            # for it to be classified as a low impact
            # performance issue
            "low": 5,

            # Max number of times a query should happen
            # for it to be classified as a warning impact
            # performance issue
            # Every query happening more times than this
            # is classified as a high impact performance issue
            "medium": 10
        }
    },

    # Path to a callback function which will be called
    # with the request, response and
    # pellet metrics object
    "callback": None
}
```

## Callback function

The callback function should accept three arguments:
1. `request` -> django request object
2. `response` -> django response object
3. `pellet_metrics` -> dict containing metrics collected by pellet

Example functionality:
1. collect and send api call level pellet metrics to an external service like datadog
2. make integration tests fail for an api if too many queries are happening by raising an exception
3. send alert emails, slack messages, etc on too many queries

### Steps:

1. Create a callback function:
```python3
# app/user/callbacks.py

from pellet.utils import get_sanitised_path

def write_datadog_metrics(path, metrics):
    # Writes metrics to datadog
    pass

def pellet_callback(request, response, pellet_metrics):
    # Get id stripped path
    # eg: /api/user/1/ -> /api/user/_id_/
    sanitised_path = get_sanitised_path(request.path)
    write_datadog_metrics(sanitised_path, pellet_metrics)
```

2. Specify the callback function in the pellet config object.
```python
PELLET = {
    # ..... rest of pellet config
    "callback": "app.user.callbacks.pellet_callback"
}
```
