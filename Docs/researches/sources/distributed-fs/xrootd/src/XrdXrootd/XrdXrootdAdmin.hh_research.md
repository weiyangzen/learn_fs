# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.hh

## Purpose

This header declares the `XrdXrootdAdmin` class that owns admin connection handling, command dispatch, job registry integration, target matching, and async response sending for the XRootD protocol server.

## Important APIs, Types, and Functions

- Public static `addJob` and `Init` are the setup API used by other protocol/configuration code.
- Public `Login` and `Start` are thread entry helpers used by the external C-style thread wrappers in the `.cc` file.
- Private command handlers cover job cancel/list, connection list/detail, and message dispatch.
- `JobTable` links admin-visible job names to `XrdXrootdJob *`.
- `usr` encodes the unsolicited response header with `kXR_attn`, action code, and payload length.

## Control Flow

`Init` starts `Start`, which accepts admin sockets and creates per-connection objects. Each connection runs `Login`, then the private command dispatch loop. The header keeps command details private so external users only register jobs and bootstrap the listener.

## State and Persistence Behavior

Static `JobList` and `eDest` are process-global. Per-connection objects hold `Stream`, `Target`, `usResp`, `TraceID`, and `reqID`. The nested `usr` constructor initializes attention framing in network byte order; action and length are filled before sends.

## Dependencies and Integration Points

The header includes `XrdLinkMatch`, `XrdOucStream`, and `XProtocol` protocol types. It forward-declares `XrdNetSocket` and `XrdXrootdJob`. `XrdXrootdProtocol.hh` declares this class as a friend, allowing admin detail reporting to inspect protocol internals.

## Risks

- Global mutable `JobList` lacks ownership and synchronization declarations.
- The public constructor/destructor are trivial, so lifecycle management of attached streams and sockets depends on method behavior.
- Fixed-size `TraceID[24]` and `reqID[16]` truncate/limit admin identities and request IDs; `.cc` rejects long request IDs but truncates login names via `strlcpy`.
- Friend access to protocol internals couples admin reporting tightly to protocol implementation layout.

## Test Signals

Compile/link tests should ensure friend access and forward declarations remain valid. Runtime tests should verify job registration before init, request ID bounds, login-name truncation behavior, response header byte order, and per-connection object cleanup after disconnect.
