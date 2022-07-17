# Pellet

Pellet helps your applications performance by warning against `N+1` queries.

The Django ORM makes it easy to forget using `select_related` and `prefetch_related` correctly and can accidentally cause `N+1` queries to happen.

Pellet ultimately aims to recreate [Bullet](https://github.com/flyerhzm/bullet) for Django.

## Installing Pellet

`pip install pellet`

## Enabling Pellet

1. Add `pellet.pellet.PelletMiddleware` to your django middleware list.
2. Configure pellet behaviour by using the `PELLET` variable in your django settings file.

## Configuring Pellet

You can configure pellet by setting the `PELLET` variable in your django settings file. The default values used by pellet if this variable or any field in the object is not found is as follows:

```
PELLET = {
    // Enable/Disable pellet
    // If set to False the pellet
    // middleware does nothing
    "enabled": False,

    // Settings related to response headers
    // set by pellet
    "headers": {

        // Enables setting response headers
        "enabled": False,

        // Header to be used for setting total query count
        "query_count_header": "X-Pellet-Count",

        // Header to be used for setting total query time
        "query_time_header": "X-Pellet-Time"
    },

    // Settings related to pellet debug mode
    "debug": {

        // Enable debug mode
        // Don't enable on prod as it will slow down your app
        "enabled": False,

        // Query count thresholds which will
        // be used by pellet to report metrics
        // on the console
        "count_threshold": {

            // Min number of times a query should happen
            // for it to be classified as N+1
            "min": 2,

            // Max number of times a query should happen
            // for it to be classified as a low impact
            // performance issue
            "low": 5,

            // Max number of times a query should happen
            // for it to be classified as a warning impact
            // performance issue
            // Every query happening more times than this
            // is classified as a high impact performance issue
            "medium": 10
        }
    }
}
```
