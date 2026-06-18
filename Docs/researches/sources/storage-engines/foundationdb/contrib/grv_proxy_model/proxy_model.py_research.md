# sources/storage-engines/foundationdb/contrib/grv_proxy_model/proxy_model.py

## Purpose
`proxy_model.py` implements a discrete-event model of FoundationDB GRV proxy request admission. It simulates request arrival, priority ordering, queueing, ratekeeper limits, limiter budget behavior, and resulting latency/throughput metrics.

## Important APIs, Types, And Functions
`Task(time, fxn)` is heap-ordered by time and represents scheduled simulation events. `Limiter` defines parameter carrier classes (`UpdateRateParams`, `UpdateLimitParams`, `CanStartParams`, `UpdateBudgetParams`) and the abstract limiter interface.

Limiter implementations model different admission policies: `OriginalLimiter` uses ratekeeper rate and a small bounded token budget; `PositiveBudgetLimiter` lets budget accumulate positively; `ClampedBudgetLimiter` caps negative debt; `TimeLimiter` and `TimePositiveBudgetLimiter` add `locked_until` throttling after overshoot; `SmoothingLimiter` uses `Smoother` to compare smoothed rate limits with smoothed releases; `SmoothingBudgetLimiter` adds a positive budget and records rich diagnostics.

`ProxyModel.Results` initializes per-priority per-second maps for starts, queues, latencies, and outstanding queue sizes plus sparse limiter diagnostic maps. `ProxyModel(duration, ratekeeper_model, workload_model, Limiter)` wires one limiter per workload priority. `run`, `update_rate`, `receive_request`, and `process_requests` drive the simulation.

## Control Flow
`run` initializes limiter rates, schedules the first request for each priority, then repeatedly pops the earliest `Task` from a heap until simulated time reaches `duration`. `update_rate` refreshes every limiter from the ratekeeper and schedules itself 0.01 seconds later. `receive_request` pushes a request into the priority heap, records queued count, and schedules the next request for that priority if the workload can produce one.

`process_requests(last_time)` computes elapsed time, updates limiter limits, then consumes queued requests while the head request's limiter permits starting it. Completing a request can re-enable a workload that was blocked by `max_outstanding`. After admission, budget updates run for all priorities using total started work, started-at-or-above-priority counts, the minimum priority admitted in the batch, last batch size, queue-empty information, and elapsed time. The method records outstanding sizes and schedules itself again after 0.001 seconds.

## State And Persistence Behavior
All state is in memory: simulated time, log time, task heap, request heap, request-scheduled flags, limiter state, workload outstanding counts, and results dictionaries. Limiter state can include rates, limits, budgets, smoothed totals, released deltas, and lockout timestamps. There is no file or database persistence.

## Dependencies And Integration Points
The model imports `Priority` for ordering and priority thresholds and `Smoother` for exponentially smoothed limiter variants. It expects `ratekeeper_model.get_limit(time, priority)`, `workload_model.priorities()`, `workload_model.next_request(time, priority)`, and `workload_model.request_completed(request)` to match the interfaces from sibling modules. `plot.py` consumes `ProxyModel.Results`.

## Risks And Edge Cases
`Task.__lt__` compares only time, so same-time event ordering is heap implementation dependent. `request_queue` is a heap of `Request` objects ordered only by priority, not arrival time within priority. `ProxyModel.Results.init_result` uses `copy.copy(starting_value)` so list values are distinct shallow copies, which works for lists but would not deeply copy nested defaults. Several limiter formulas divide by `self.rate`; a zero rate can cause failures in time-based limiter overshoot paths. Assertions require each workload to produce an initial request.

## Test Signals
Tests should run deterministic workloads/ratekeepers and assert queued counts, started counts, latency buckets, lockout behavior, and budget diagnostics. Good regression signals include starvation behavior for batch traffic, max outstanding backpressure, zero-rate workloads, fixed-rate throughput, and deterministic output under seeded request distributions.
