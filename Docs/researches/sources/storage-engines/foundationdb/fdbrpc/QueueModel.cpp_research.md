# sources/storage-engines/foundationdb/fdbrpc/QueueModel.cpp

`QueueModel.cpp` maintains per-endpoint queue measurements used by load-balanced request selection and future-version backoff.

`addRequest()` adds the endpoint penalty into smoothed outstanding work and returns the penalty. `endRequest()` removes the outstanding delta, updates latency, adjusts future-version backoff and failed-until time, and records a positive new penalty. `getMeasurement()` returns `QueueData`. TSS metadata helpers update/remove/read optional `TSSEndpointData`. Reply adapter overloads convert typed reply pointers to optional load-balance metadata.

Control flow is request lifecycle accounting: add penalty before dispatch, remove it on completion, replace latency for clean results or keep the maximum for unclean results. Future-version responses grow backoff exponentially up to a knob cap and set endpoint failure time; clean non-future-version responses reset that backoff.

State is an in-memory endpoint-ID map of `QueueData`, including latency, penalty, smoothed outstanding work, backoff fields, failed-until time, and optional TSS data. Dependencies include `QueueModel.h`, `LoadBalance.h`, Flow time, and knobs.

Risks include `data[id]` mutating state on reads, timing-sensitive backoff behavior, and penalty updates only when positive. There are no direct tests in this file; behavior is indirectly covered by load-balanced request and simulation scenarios.
