# sources/storage-engines/foundationdb/contrib/grv_proxy_model/plot.py

## Purpose
`plot.py` visualizes the GRV proxy simulation results produced by `proxy_model.py`. It turns per-priority request, queue, latency, limiter rate, limiter budget, and release-time series into a fixed 3x3 matplotlib dashboard.

## Important APIs, Types, And Functions
The central API is `Plotter(results)`, where `results` is expected to be a `ProxyModel.Results` instance with dictionaries such as `started`, `queued`, `latencies`, `unprocessed_queue_sizes`, `rate`, `released`, `limit`, `limit_and_budget`, and `budget`. `Plotter.add_plot(data, time_resolution, label, use_avg=False)` buckets numeric values by `t // time_resolution * time_resolution`; `Plotter.add_plot_with_times(data, label)` plots raw ordered key/value series; `display(time_resolution=0.1)` lays out the dashboard.

## Control Flow
`display` creates a large figure, draws request starts, queued requests, and maximum unprocessed queue sizes in the first row, then allocates one subplot per priority for latency percentiles and one subplot per priority for limiter/rate/budget diagnostics. Latencies are derived by selecting median, 90th percentile, and max values from per-second latency lists before plotting. The function ends with `plt.show()`.

## State And Persistence Behavior
The module does not persist data. It reads the supplied result object, aggregates values in local dictionaries, and mutates only matplotlib global plotting state. It assumes latency vectors are already ordered by append order and uses integer-second keys present in `ProxyModel.Results`.

## Dependencies And Integration Points
It depends on `matplotlib.pyplot` and the shape of `ProxyModel.Results`. It integrates with `priority.Priority` only indirectly through dictionary keys, whose `__str__` labels appear in legends and y-axis text.

## Risks And Edge Cases
`add_plot` and `add_plot_with_times` are defined without `self`, so they must be called as class functions as this file does. Latency percentile lookup does not sort samples and can fail to represent real percentiles if completion latencies are not appended in sorted order. The fixed 3x3 grid can overflow if more priorities or limiter series are added. Empty dicts produce empty plots, but latency lists are guarded.

## Test Signals
Useful tests would construct synthetic `ProxyModel.Results`, call `display` under a noninteractive matplotlib backend, and assert expected subplot/line counts and bucketed values. Current signals are mostly manual: rendered charts should show queued/started rates, queue sizes, latency curves, and limiter budgets per priority.
