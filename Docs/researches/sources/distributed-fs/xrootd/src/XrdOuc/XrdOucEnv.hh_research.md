# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.hh

## Purpose
Declares `XrdOucEnv`, a container for XRootD extended environment variables plus optional security entity context.

## Important APIs, Types, And Functions
Public methods include `Env`, `EnvTidy`, static `Export`/`Import`, `Get`, `GetInt`, `GetPtr`, `Put`, `PutInt`, `PutPtr`, `Delimit`, and `secEnv`. The object stores an `XrdOucHash<char>` for variable values, a non-owned `XrdSecEntity` pointer, and the copied raw environment string.

## Control Flow
Callers construct from a serialized variable string, then query typed values or mutate hash entries. `Env` returns the original normalized blob; `EnvTidy` returns a sanitized version suitable for contexts that should not expose authorization data.

## State And Persistence
The class owns `global_env` and hash values. The security entity pointer is non-owned. Static `Export` affects the process environment outside the object.

## Dependencies And Integration Points
Includes `XrdOucHash.hh` and forward-declares `XrdSecEntity`. It is used by plugins, request handlers, and stream/config utilities that need structured environment metadata.

## Risks And Test Signals
Risks include returning mutable internal pointers, no synchronization, ownership assumptions for `secEntity`, and caller responsibility not to free returned hash strings. Test signals are constructor/destructor memory checks, hash replacement cleanup, and callers using `EnvTidy` before logging request environments.
