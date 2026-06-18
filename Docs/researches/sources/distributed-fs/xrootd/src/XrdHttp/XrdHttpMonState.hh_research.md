
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMonState.hh

## Purpose

`XrdHttpMonState.hh` defines the request-local monitoring lifecycle enum used by `XrdHttpReq` and `XrdHttpMon` to classify outcomes across multi-step HTTP responses.

## Important APIs, Types, And Functions

- `enum class XrdHttpMonState : int` has five values:
  - `NEW`: request has not yet been counted.
  - `ACTIVE`: initial response has started and final outcome is pending.
  - `ERR_NET`: socket/TLS send failure should be recorded as a network error.
  - `ERR_PROT`: backend/protocol failure after a valid HTTP response began.
  - `DONE`: final monitoring record has been emitted.

## Control Flow

`XrdHttpReq::reset()` initializes `monState` to `NEW`. `XrdHttpMon::Record()` transitions `NEW` to `ACTIVE` on the first final response code and then transitions active/error states to `DONE`. `XrdHttpProtocol::SendData()` sets `ERR_NET` on failed send. `XrdHttpProtocol::ChunkResp()` sets `ERR_PROT` for final chunked responses when the bridge indicates `kXR_error` and monitoring is still `ACTIVE`.

## State And Persistence

The enum itself is stateless; persistence is the `XrdHttpReq::monState` field for a single request. It is intentionally reset per request and has no durable storage.

## Dependencies And Integration Points

It is included by `XrdHttpReq.hh`, and indirectly consumed by `XrdHttpMon.cc` and `XrdHttpProtocol.cc`. The file has no external dependencies beyond include guards.

## Risks And Edge Cases

- Correct classification depends on every response path calling `XrdHttpMon::Record()` in the expected order.
- Network errors before the first monitoring call may be represented differently than failures after `ACTIVE`.
- `DONE` duplicate detection is logging-only, so over-calling remains a correctness risk for metrics consumers.

## Test Signals

Tests should force simple response success, failed socket send, chunked response backend error, and duplicate finalization to confirm the expected `Record()` classification. Reset behavior should be verified by reusing an `XrdHttpReq` object across requests.
