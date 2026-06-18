# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAdmin.cc

## Purpose

This file implements the XRootD admin control channel. It accepts admin socket connections, performs a text login handshake, processes admin commands, lists client/job state, cancels jobs, and sends asynchronous messages to matching client links.

## Important APIs, Types, and Functions

- External thread entry points `XrdXrootdInitAdmin` and `XrdXrootdLoginAdmin`.
- Static setup: `XrdXrootdAdmin::Init` starts the accept loop, and `addJob` registers cancel/list capable job types.
- Connection handling: `Start` accepts sockets forever, `Login` attaches a socket to `XrdOucStream`, validates `<reqid> login <name>`, and enters `Xeq`.
- Command handlers: `do_Cj`, `do_Lsc`, `do_Lsd`, `do_Lsj`, `do_Lsj_Xeq`, and `do_Msg`.
- Helpers: `getMsg`, `getreqID`, `getTarget`, `sendErr`, `sendOK`, and `sendResp` overloads.

## Control Flow

`Init` stores the shared error logger and starts an admin accept thread. `Start` loops on `AdminSock->Accept()` and starts a per-connection login thread. `Login` attaches the accepted descriptor to `Stream`, requires an initial login command, records `TraceID`, logs success, and invokes `Xeq`. `Xeq` reads request lines formatted as `<msgid> <cmd> <args>`, dispatches known commands, and exits on stream EOF or handler failure.

`do_Cj` and `do_Lsj` select a registered `XrdXrootdJob` by name or `*`, then cancel or list jobs. `do_Lsc` lists matching client names via `XrdLink::getName`. `do_Lsd` finds matching `XrdLink` objects, dynamic-casts their protocol to `XrdXrootdProtocol`, and emits XML-like connection, monitoring, auth, and I/O stats. `do_Msg` targets links and sends a `kXR_asyncms` response with or without payload.

## State and Persistence Behavior

Process-global state includes static `eDest` and `JobList`. Each admin connection owns an `XrdOucStream`, `XrdLinkMatch` target matcher, reusable `usResp` response header, `TraceID`, and `reqID`. State is in memory only; admin commands observe live server links and jobs rather than persisted data.

## Dependencies and Integration Points

The file depends on `XrdNetSocket`, `XrdSysThread`, `XrdOucStream`, `XrdLink`, `XrdLinkMatch`, `XrdXrootdJob`, `XrdXrootdProtocol`, XRootD protocol constants from `XProtocol`, and tracing through `XrdXrootdTrace`. It is initialized from XRootD configuration code when an admin socket is configured.

## Risks

- `Start` passes `&InSock` to a newly spawned thread; the stack variable can change before `XrdXrootdLoginAdmin` dereferences it, causing wrong or duplicate descriptors under rapid accepts.
- `JobList` is a global linked list with no locking; concurrent `addJob`, cancel, and list operations can race if registration is not strictly startup-only.
- XML-like responses interpolate client/admin-controlled strings without escaping, so names, hosts, roles, or messages containing markup can break response syntax.
- The accept loop is infinite with no shutdown path in this file.
- `do_Lsd` reference management depends on `XrdLink::Find` semantics; it calls `setRef(-1)` only on one error branch.
- Authentication/authorization of admin socket users is not visible here and must be enforced by socket exposure or upstream config.

## Test Signals

Integration tests should exercise login success/failure, each command (`cj`, `lsc`, `lsd`, `lsj`, `msg`), wildcard job handling, invalid job types, malformed request IDs, target parsing, client data containing XML special characters, rapid concurrent admin connects to expose the socket-FD race, and admin disconnect logging.
