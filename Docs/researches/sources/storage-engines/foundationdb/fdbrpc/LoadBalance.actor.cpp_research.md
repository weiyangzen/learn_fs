# sources/storage-engines/foundationdb/fdbrpc/LoadBalance.actor.cpp

`LoadBalance.actor.cpp` throttles repeated `all_alternatives_failed` errors so clients do not saturate proxies with location-refresh requests.

The exported actor is `allAlternativesFailedDelay(Future<Void> okFuture)`. It reads and updates `g_network->networkInfo` timestamps and uses knobs for reset time, minimum delay, skip delay, delay ratios, and maximum delays.

Control flow computes a delay based on the elapsed failure window unless the skip-delay interval allows immediate behavior. It records the newest failure time, races `okFuture` against `delayJittered(delay)`, and throws `all_alternatives_failed()` only if the delay wins. If `okFuture` completes first, the actor returns without error.

State is transient process-global network info, with no persistence. Dependencies include `LoadBalance.actor.h`, Flow actors/coroutines, `g_network`, and Flow knobs. Higher-level load-balanced RPC code interprets the thrown error as a signal to refresh key locations.

Risks are tuning-related: delays that are too small can overload proxies, while delays that are too high slow recovery from stale alternatives. Process-global timestamps also mean one workload can influence another in the same process. Coverage is indirect through load-balancing and simulation workloads.
