
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.cc

## Purpose

`XrdHttpMon.cc` implements the global HTTP monitoring collector for the XrdHTTP protocol plugin. It records per-request operation/status metrics for the `XrdXrootdGStream` JSON monitoring path and simpler verb/status counters for `XrdMonRoll`. The implementation is process-global and is initialized from `XrdHttpProtocol::Config()` when either monitoring integration is present in the protocol environment.

## Important APIs, Types, And Functions

- Static storage: `statsInfo`, `verbCounters`, `statusCounters`, `statsSchema`, `gStream`, `mrollP`, `flushPeriod`, `hasGStream`, `hasMonRoll`, and `isInitialized`.
- `Initialize(logP, gStream, mrollP)` wires logging, stores monitoring sinks, derives `flushPeriod` from `gStream->GetAutoFlush()`, registers the MonRoll schema, and marks monitoring initialized.
- `Start(void*)` is the background thread entry point. It sleeps for `flushPeriod` and repeatedly calls `Report()`.
- `Report()` serializes `GetMonitoringJson()` and inserts it into the GStream buffer.
- `Record(XrdHttpReq &req, int code)` is the central request lifecycle hook used by `XrdHttpProtocol` response senders. It ignores interim codes under 200, validates `req.request`, derives `StatusCodes`, and advances `req.monState`.
- `RecordCount()`, `RecordSuccess()`, `RecordErrProt()`, and `RecordErrNet()` update the GStream matrix.
- `GetMonitoringJson()` emits keys like `HTTP_GET_200` containing count, network error count, xrootd/protocol error count, success count, and total duration in seconds.
- `GetOperationString()`, `GetStatusCodeString()`, and `ToStatusCode()` map sparse public request/status codes into compact monitoring dimensions.

## Control Flow

Initialization is opt-in. `XrdHttpProtocol::Config()` passes GStream and MonRoll pointers from `XrdOucEnv`; if GStream is enabled it also starts `XrdHttpMon::Start()` on a thread. Normal response paths call `XrdHttpMon::Record()` from `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, and network-error branches. `Record()` uses `XrdHttpMonState` as a small state machine: `NEW` records the request count and verb, `ACTIVE` records success and status, `ERR_NET` records network failure, `ERR_PROT` records backend/protocol failure after an HTTP response has begun, and `DONE` logs an unexpected duplicate record.

The GStream accounting intentionally splits total request count from final outcome. A response start records count by transitioning `NEW` to `ACTIVE`; final send or final chunk records success or error and transitions to `DONE`. MonRoll records only request verb at the first transition and status at final outcome transitions.

## State And Persistence

All counters are static process memory backed by `RAtomic_uint64_t`; resets only happen on process restart. `statsSchema` stores references to the MonRoll counters and must stay aligned with `XrdHttpReq::ReqType` and `StatusCodes`. `req.monState` and `req.startTime` live per request and are reset in `XrdHttpReq::reset()`. There is no on-disk persistence.

## Dependencies And Integration Points

This file depends on `XrdHttpMon.hh`, `XrdHttpReq.hh`, `XrdSysError`, `XrdXrootdGStream`, `XrdMonRoll`, C++ atomics wrappers, and `std::chrono`. It integrates with protocol response sending in `XrdHttpProtocol.cc`, request lifecycle state from `XrdHttpMonState.hh`, and request verb definitions in `XrdHttpReq.hh`.

## Risks And Edge Cases

- `Start()` loops forever and assumes a nonzero `flushPeriod`; with GStream enabled this is normally set, but defensive handling is minimal.
- `Report()` dereferences `gStream`; it is only started when GStream exists, so misuse outside `Config()` would be unsafe.
- MonRoll schema uses fixed enum index positions. Adding or reordering `XrdHttpReq::ReqType` without updating this mapping corrupts monitoring labels.
- `GetOperationString()` does not explicitly map `rtOPTIONS`, `rtPATCH`, `rtPOST`, or `rtCOPY`, so GStream may classify those as `UNKNOWN` while MonRoll has counters for them.
- Duration accumulation casts an atomic count through `std::chrono::microseconds` and then `std::chrono::duration<double>`; the variable name `duration_us` in `GetMonitoringJson()` is misleading because the JSON field is seconds.
- Duplicate calls after `DONE` only log; they do not repair counters.

## Test Signals

Useful tests should cover status-code mapping, verb mapping alignment, no-op behavior before initialization, state transitions `NEW -> ACTIVE -> DONE`, network/protocol error transitions, interim `100 Continue` not being counted as final, JSON serialization skipping zero-count entries, and MonRoll schema alignment when `ReqType` changes. An integration test can simulate `SendSimpleResp()` and chunked response paths with a fake request and monitoring sink.
