<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh

## Purpose

`XrdPfcDecision.hh` declares the plugin interface used by XrdPfc to decide whether a source file should be cached.

## Important APIs, Types, And Functions

- `XrdPfc::Decision` is an abstract base class with a virtual destructor.
- `Decide(const std::string&, XrdOss&) const` is the required runtime policy method.
- `ConfigDecision(const char *params)` is an optional configuration hook with a default success implementation.

## Control Flow

`Cache::xdlib()` loads a shared object, resolves `XrdPfcGetDecision`, constructs a `Decision`, optionally calls `ConfigDecision()`, and stores it. `Cache::Decide()` then requires every configured decision object to return true before wrapping an IO in the cache.

## State And Persistence

The base class has no state. Implementations may store policy data and may inspect the `XrdOss` namespace during decisions.

## Dependencies And Integration Points

It forward-declares `XrdOss` and `XrdSysError` and includes `string`. External plugins must export `XrdPfcGetDecision(XrdSysError&)` returning a `Decision*`.

## Risks And Edge Cases

- The loader currently does not reject a plugin whose `ConfigDecision()` returns false.
- Runtime decisions are synchronous on the attach path, so slow policy checks can delay file opens.
- The interface returns only boolean allow/deny, with no reason code for diagnostics.

## Test Signals

Tests should verify ABI-compatible plugin loading, default `ConfigDecision()` behavior, multiple decision plugins combining by logical AND, and handling of null plugin pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh -->
