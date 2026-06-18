# sources/storage-engines/foundationdb/contrib/grv_proxy_model/workload_model.py

## Purpose
`workload_model.py` generates request streams for the GRV proxy simulator. It models per-priority arrivals, batch sizes, inter-arrival distributions, and outstanding-request backpressure.

## Important APIs, Types, And Functions
`Request(time, count, priority)` is heap-ordered by priority. `PriorityWorkloadModel` combines a priority, rate model, batch generator, request interval generator, and `max_outstanding`. `next_request(time)` returns a future `Request` or `None` when outstanding work is capped; `request_completed(request)` decrements outstanding count and reports whether generation should resume.

`WorkloadModel` wraps a priority-to-model map. `Distribution` provides `exponential`, `uniform`, and `fixed` callables. `DistributionBatchGenerator.next_batch()` returns `ceil(distribution(size))`. `DistributionRequestGenerator.next_request_interval(rate)` returns a sampled interval based on `1/rate` or `1e9` for zero rate. `predefined_workloads` defines named scenarios including `slow_exponential`, `fixed_uniform`, `batch_starvation`, `default_low_high_low`, and several fixed default rates.

## Control Flow
The simulator asks a priority workload for its next request. If outstanding work is at or above the cap, generation pauses. Otherwise a batch size is sampled, outstanding count increases immediately, an interval is sampled from the current rate, and a request at `time + interval` is returned. When the proxy admits a request, `request_completed` reduces outstanding work and returns true only when the workload was previously full and has dropped below the cap.

## State And Persistence Behavior
Outstanding counts live in each `PriorityWorkloadModel`. Distribution and interval rate models may hold their own state. The wrapper and predefined workload dictionaries are in memory only; no persistence occurs.

## Dependencies And Integration Points
The module imports `numpy`, `math`, sibling `rate_model`, and `Priority`. `proxy_model.ProxyModel` uses the `WorkloadModel` interface for scheduling and backpressure. `plot.py` later reads outstanding sizes captured by `ProxyModel`.

## Risks And Edge Cases
`Request.__lt__` ignores time and count, so queued request heap order is strictly priority-based with unspecified same-priority ordering. `DistributionBatchGenerator` can return zero for uniform distributions near zero, creating requests with no work but still affecting outstanding logic. Negative or nonsensical distribution results are not guarded. Zero request rate maps to a very large delay instead of no request.

## Test Signals
Tests should cover outstanding cap behavior, resume-on-completion logic, deterministic fixed distributions, random distributions under seeded numpy, zero rate behavior, batch rounding, and priority ordering in the request heap.
