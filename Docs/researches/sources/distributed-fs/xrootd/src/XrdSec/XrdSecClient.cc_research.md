# sources/distributed-fs/xrootd/src/XrdSec/XrdSecClient.cc

## Purpose

`XrdSecClient.cc` exposes the client-side security protocol selection entrypoint and a no-authentication fallback protocol.

## Important APIs, Types, And Functions

- Local `XrdSecProtNone` implements `XrdSecProtocol` with no-op `Authenticate()`, empty credentials from `getCredentials()`, and no deletion because it is static.
- Exported `extern "C" XrdSecGetProtocol(hostname, endPoint, parms, einfo)` returns `ProtNone` when the server requests no security, otherwise asks static `XrdSecPManager` to load/select a supported protocol.
- Static `DebugON` is driven by `XrdSecDEBUG`.
- Static `XrdSecPManager` is constructed with proxy flags from `XrdSecPROXY` and `XrdSecPROXYCREDS`.

## Control Flow

Client code calls `XrdSecGetProtocol()` with server parameters. If `parms` is empty, the static no-auth protocol is returned. Otherwise the protocol manager locates a matching security plugin. Failure sets `ENOPROTOOPT` in `einfo` or logs to stderr.

## State And Persistence

The fallback protocol and protocol manager are static process-lifetime objects. Debug/proxy behavior is captured on first function call from environment variables.

## Dependencies And Integration Points

It depends on `XrdSecPManager`, `XrdSecInterface`, `XrdNetAddrInfo`, and `XrdOucErrInfo`. It is loaded from the client-facing security module and is influenced by PSS setting `XrdSecPROXY=1`.

## Risks And Edge Cases

- Environment variables are read once due to static initialization inside the function.
- `XrdSecProtNone::Delete()` intentionally does nothing; consumers must not expect ownership.
- Debug output can include raw security tokens in stderr when enabled.

## Test Signals

Tests should call with empty parameters and expect the no-auth protocol, call with unsupported parameters and expect `ENOPROTOOPT`, and verify proxy/debug environment behavior before first call.
