# sources/storage-engines/foundationdb/fdbclient/RESTClient.cpp

## Purpose
`RESTClient.cpp` implements a generic asynchronous REST client on top of FoundationDB Flow networking and `fdbrpc/HTTP`. It parses URLs through `RESTUrl`, obtains pooled TCP/TLS connections, sends HTTP requests, retries selected failures, and records per-host statistics.

## Important APIs, Types, and Functions
- `RESTClient::Stats::getJSON`, `operator-`, and `clear` expose per `host:service` counters for successes, failures, and bytes sent.
- Constructors initialize a `RESTConnectionPool` with knob-derived pool size and optionally apply knob overrides.
- `setKnobs` and `getKnobs` delegate to `RESTClientKnobs`.
- `isErrorRetryable` decides which Flow errors should be retried by this client. The current implementation returns false for timeout and connection failure.
- `doRequest_impl` builds `HTTP::OutgoingRequest`, fills host/resource/body, obtains a pooled connection, performs `HTTP::doRequest`, handles connection reuse, classifies errors/status codes, backs off, and throws typed HTTP/connection errors.
- Public verb helpers are `doGet`, `doHead`, `doDelete`, `doTrace`, `doPut`, and `doPost`.

## Control Flow and State
For each request, `doRequest_impl` creates one request object and loops until success, non-retryable failure, or tries are exhausted. It checks out a `ReusableConnection`, applies connect and request timeouts separately, returns healthy keep-alive connections unless the response says `Connection: close`, and closes checked-out connections on exceptions to satisfy simulation connection assertions. Failures increment stats, emit throttled trace events, optionally honor `Retry-After`, and use exponential retry delay capped at 60 seconds.

## State and Persistence Behavior
State is process-local: knobs, connection pool, and `statsMap`. It does not persist request state. Reused connections are keyed by `host:service` and expire according to `max_connection_life`.

## Dependencies and Integration Points
The implementation depends on `RESTUtils` for URL parsing, knobs, and connection pooling; `fdbrpc/HTTP` for wire protocol; Flow actors, packet queues, rate controls, tracing, and unit tests. Higher-level clients, including blob-store code, can reuse this client pattern or its utilities.

## Risks and Edge Cases
- `doGetHeadDeleteOrTrace` accepts a `verb` argument but calls `doRequest_impl` with `HTTP::HTTP_VERB_GET`, so `HEAD`, `DELETE`, and `TRACE` requests appear to be sent as GET. This is a high-value regression test target.
- The retry classification comment says unreachable or timed-out servers should bubble to callers, and the implementation does not retry timeout/connection_failed even though the variable name can be confusing.
- `HTTP_STATUS_CODE_BAD_GATEWAY` is listed twice in retryable status checks.
- `TOO_MANY_REQUESTS` does not increment `thisTry`, so persistent 429s can continue beyond the nominal try count, bounded mainly by actor cancellation or external timeouts.
- Request body content is written once before retries; this is safe only because the request owns an `UnsentPacketQueue` that remains valid for the loop.

## Test Signals
The file includes a unit test for knob defaults, mutation, and invalid knob errors. Additional important tests should cover verb preservation for HEAD/DELETE/TRACE, `Retry-After`, 429 retry behavior, connection reuse/drop on `Connection: close`, timeout mapping to `connection_failed`, and stats counter updates.
