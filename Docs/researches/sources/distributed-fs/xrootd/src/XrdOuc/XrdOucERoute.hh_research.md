# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.hh

## Purpose
Declares `XrdOucERoute`, a stateless formatter/router for standard XRootD error messages.

## Important APIs, Types, And Functions
Static methods are `Format(char*, int, int, const char*, const char*, const char*)` and `Route(XrdSysError*, XrdOucStream*, const char*, int, const char*, const char*)`. Forward declarations avoid pulling in full stream/error definitions.

## Control Flow
Consumers call `Format` for buffer-only use or `Route` to both format and emit to selected destinations.

## State And Persistence
No state. Constructing an `XrdOucERoute` object is unnecessary but supported by trivial constructor/destructor.

## Dependencies And Integration Points
Integrates `XrdSysError` logging with `XrdOucStream` client/config streams. The contract specifies negative errno returns.

## Risks And Test Signals
Risks are declaration drift against the `.cc` implementation and callers passing undersized buffers. Build coverage and formatting tests are sufficient for this header.
