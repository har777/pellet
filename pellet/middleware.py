import logging
import time
from importlib import import_module

from django.conf import settings
from django.db import connection
from rich import box
from rich import print as rich_print
from rich.table import Table

logger = logging.getLogger(__name__)


class PelletMetrics:
    def __init__(self):
        # count of number of queries run
        self.count = 0
        # total time taken to run those queries
        self.elapsed_time = 0
        # stats per query
        self.query_stats = {}

    def __call__(self, execute, sql, params, many, context):
        self.count += 1
        start = time.monotonic()
        result = execute(sql, params, many, context)
        elapsed_time = time.monotonic() - start
        self.elapsed_time += elapsed_time

        if getattr(settings, "PELLET", {}).get("query_level_metrics_enabled", False):
            if sql not in self.query_stats:
                self.query_stats[sql] = {"count": 0, "elapsed_time": 0}
            self.query_stats[sql]["count"] += 1
            self.query_stats[sql]["elapsed_time"] += elapsed_time

        return result


class PelletMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_color_prefix(count: int):
        if count <= getattr(settings, "PELLET", {}).get("debug", {}).get(
            "count_threshold"
        ).get("low", 5):
            return "[bold green]"
        elif count <= getattr(settings, "PELLET", {}).get("debug", {}).get(
            "count_threshold"
        ).get("medium", 10):
            return "[bold yellow]"
        else:
            return "[bold red]"

    def __call__(self, request):
        # Skip pellet if disabled
        if not getattr(settings, "PELLET", {}).get("enabled", False):
            return self.get_response(request)

        pellet_metrics = PelletMetrics()
        with connection.execute_wrapper(pellet_metrics):
            response = self.get_response(request)

        # Skip pellet metrics processing if path doesn't resolve
        if not request.resolver_match:
            return response

        count = pellet_metrics.count
        elapsed_time = float(format(pellet_metrics.elapsed_time, ".3f"))

        # Add pellet metrics to the response header if enabled
        if getattr(settings, "PELLET", {}).get("headers", {}).get("enabled", False):
            response[
                getattr(settings, "PELLET", {})
                .get("headers", {})
                .get("query_count_header", "X-Pellet-Count")
            ] = count
            response[
                getattr(settings, "PELLET", {})
                .get("headers", {})
                .get("query_time_header", "X-Pellet-Time")
            ] = elapsed_time

        if getattr(settings, "PELLET", {}).get("callback", None):
            callback_path = getattr(settings, "PELLET", {}).get("callback")
            try:
                callback_path_split = callback_path.split(".")
                module_name = ".".join(callback_path_split[:-1])
                func_name = callback_path_split[-1]
                callback_func = getattr(import_module(module_name), func_name)
                callback_func(
                    request=request,
                    response=response,
                    pellet_metrics=pellet_metrics.__dict__,
                )
            except (AttributeError, IndexError, ModuleNotFoundError):
                logger.exception(
                    "Pellet callback: {callback_name} failed".format(
                        callback_name=callback_path
                    )
                )

        if getattr(settings, "PELLET", {}).get("debug", {}).get("enabled", False):
            pellet_title = "{color_prefix}{method} {path} : {count} {query_word} in {elapsed_time}s".format(
                color_prefix=self.get_color_prefix(count=count),
                method=request.method,
                path=request.get_full_path(),
                count=count,
                query_word=("query" if count == 1 else "queries"),
                elapsed_time=elapsed_time,
            )

            pellet_table = Table(
                title=pellet_title,
                show_header=True,
                header_style="bold white",
                show_lines=True,
                box=box.ASCII_DOUBLE_HEAD,
                min_width=100,
            )

            pellet_table.add_column("N+1 Query")
            pellet_table.add_column("Count", justify="right")
            pellet_table.add_column("Time(sec)", justify="right")

            query_stats = pellet_metrics.query_stats

            # Sort by decreasing value of count and elapsed_time
            query_stats = dict(
                sorted(
                    query_stats.items(),
                    key=lambda item: (item[1]["count"], item[1]["elapsed_time"]),
                    reverse=True,
                )
            )

            for query, stats in query_stats.items():
                # N+1 query
                if stats["count"] >= getattr(settings, "PELLET", {}).get(
                    "debug", {}
                ).get("count_threshold", {}).get("min", 2):
                    color_prefix = self.get_color_prefix(count=stats["count"])
                    pellet_table.add_row(
                        "{color_prefix}{query}".format(
                            color_prefix=color_prefix, query=query
                        ),
                        "{color_prefix}{count}".format(
                            color_prefix=color_prefix, count=stats["count"]
                        ),
                        "{color_prefix}{elapsed_time}".format(
                            color_prefix=color_prefix,
                            elapsed_time=format(stats["elapsed_time"], ".3f"),
                        ),
                    )

            # If query level metrics was disabled
            if not getattr(settings, "PELLET", {}).get(
                "query_level_metrics_enabled", False
            ):
                pellet_table.add_row(
                    "[bold green]Query level metrics disabled",
                    "",
                    "",
                )
            # If no N+1 found
            elif pellet_table.row_count == 0:
                pellet_table.add_row(
                    "[bold green]No N+1 queries detected",
                    "",
                    "",
                )

            rich_print(pellet_table)

        return response
