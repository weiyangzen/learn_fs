## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/QueueModel.h

Purpose: Declares the client-side queue/latency model used by load balancing to estimate endpoint load, penalize overloaded servers, delay retrying failed/future-version endpoints, and manage TSS endpoint mappings.

Important APIs/types/functions: `TSSEndpointData` maps a storage endpoint to a TSS endpoint and metrics. `QueueData` stores `Smoother smoothOutstanding`, last latency, server penalty, `failedUntil`, future-version backoff state, and optional TSS mapping. `QueueModel` exposes `addRequest()`, `endRequest()`, `getMeasurement()`, TSS update/remove/get methods, secondary-request budget/multiplier fields, and actor collections for lagging requests and TSS comparisons.

Control flow: `loadBalance()` calls `addRequest()` when issuing an attempt and `endRequest()` when a response/error is classified. The model exposes measurements used to choose best/next endpoints and to compute second-request delays. Lagging request and TSS actor collections are fed from load-balance code to keep accounting asynchronous but bounded.

State and persistence behavior: All state is in-memory per client/process. The `data` map is keyed by endpoint token id. Destructor cancels lagging/TSS actor collections. No durable persistence.

Dependencies and integration points: Depends on `Smoother`, Flow knobs, `ActorCollection`, `TSSComparison`, and `FlowTransport::Endpoint`. It is directly integrated with `LoadBalance.actor.h`.

Risks: Incorrect `delta` pairing between `addRequest()` and `endRequest()` corrupts outstanding estimates. Future-version and failed-until backoff influence endpoint exclusion, so bad tuning can underuse healthy replicas. `laggingTSSCompareCount` is declared but not initialized in the constructor in this header, making implementation/constructor initialization worth checking.

Test signals: Model tests should assert outstanding smoothing deltas, penalty updates, latency updates, failure/future-version backoff, endpoint measurement creation, secondary request budget changes, TSS mapping lifecycle, and actor collection cancellation.
