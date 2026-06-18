
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.hh

## Purpose

`XrdHttpMon.hh` declares the static monitoring facade used by XrdHTTP to collect request and response metrics. It exposes a small public API for initialization, background reporting, and response-path recording while hiding the global counter tables and mapping helpers.

## Important APIs, Types, And Functions

- `enum StatusCodes` defines a compact, dense set of monitored HTTP status buckets plus `sc_UNKNOWN` and `sc_Count`.
- `struct HttpInfo` stores cumulative atomic counters: total count, network errors, XRootD/protocol errors, successes, and summed duration in microseconds.
- `Initialize(XrdSysLogger*, XrdXrootdGStream*, XrdMonRoll*)` configures monitoring sinks.
- `Start(void*)` is the thread entry point for periodic GStream flushing.
- `Record(XrdHttpReq&, int)` is the only public per-response update API.
- `IsInitialized()` lets callers cheaply test global setup state.
- Private helpers `Record*`, `RecordGStream*`, and `RecordMonRoll*` keep runtime overhead low when a monitoring backend is disabled.

## Control Flow

The header establishes a split backend model. When GStream exists, the detailed `statsInfo[ReqType][StatusCodes]` matrix is updated and periodically serialized. When MonRoll exists, only `verbCounters` and `statusCounters` are incremented through a registered schema. The inline conditional helpers are intended to compile down to fast checks in response hot paths.

## State And Persistence

All state is static and process-wide. The stats matrix is indexed by `XrdHttpReq::ReqType::rtCount` and `StatusCodes::sc_Count`; `statsSchema` refers to static atomic counters. The class cannot be instantiated or destroyed by consumers.

## Dependencies And Integration Points

The header includes `Xrd/XrdMonRoll.hh`, `XrdHttpReq.hh`, `XrdSys/XrdSysRAtomic.hh`, and standard `array`, `chrono`, `string`, and `vector`. It forward-declares `XrdXrootdGStream` and `XrdSysLogger`. It is included by `XrdHttpProtocol.cc` and implemented by `XrdHttpMon.cc`.

## Risks And Edge Cases

- Public declarations depend on `XrdHttpReq.hh`, so changes to request type definitions can break monitoring dimensions.
- The dense `StatusCodes` enum must remain synchronized with `ToStatusCode()` and `statsSchema`.
- Static mutable members imply global lifetime and thread-safety concerns; counter fields are atomic but configuration flags and pointers are plain static values set during startup.
- `RecordMonRollVerb()` and `RecordMonRollStatus()` index arrays directly and rely on prior range checks in `Record()`.

## Test Signals

Header-level compatibility tests should compile with modified `ReqType` values and fail if schema/index assumptions are stale. Unit tests should exercise `IsInitialized()`, conditional updates when only one backend is enabled, and atomic counter increments through the public `Record()` path rather than private helpers.
