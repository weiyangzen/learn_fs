## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TimedRequest.h

Purpose: Provides a base/helper carrying the server-side request receipt time for RPC request structs.

Important APIs/types/functions: `TimedRequest` stores `_requestTime`, exposes `requestTime()` with an assertion that it is positive, and `setRequestTime()`. Its constructor records `g_network->timer()` when not running as a client; clients initialize time to zero.

Control flow: Construction decides whether to stamp the request based on `FlowTransport::isClient()`. Consumers can later read the request time after server-side construction or explicit setting.

State and persistence behavior: Only per-request in-memory timestamp state. No serialization is defined in this header; derived request serialization must handle any required timing fields separately if needed.

Dependencies and integration points: Depends on Flow network and `fdbrpc.h` for `FlowTransport`. Request types can inherit or embed it to measure request queue/processing latency.

Risks: Calling `requestTime()` on a client-created object before `setRequestTime()` asserts. The timer source is process-local/simulation aware; comparisons must use compatible clocks.

Test signals: Client vs server constructor behavior, explicit `setRequestTime()`, assertion coverage for unset reads, and latency measurement integration in request handlers.
