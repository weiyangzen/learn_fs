# sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.cc

## Purpose

This file implements the XrdCl socket wrapper. It provides nonblocking TCP setup, connect helpers, blocking raw read/write loops, async-friendly send/read wrappers, polling, peer-name caching, errno classification, TCP corking, and TLS handshaking support.

## Important APIs, Types, And Functions

Key methods are constructor/destructor, `Initialize`, `SetFlags`, `GetFlags`, `GetSockOpt`, `SetSockOpt`, `Connect`, `ConnectToAddress`, `Close`, `ReadRaw`, `WriteRaw`, overloads of `Send`, `Poll`, `GetSockName`, `GetPeerName`, `GetName`, `ClassifyErrno`, `Read`, `ReadV`, `Cork`, `Uncork`, `Flash`, `MapEvent`, `TlsHandShake`, and `IsEncrypted`.

## Control Flow

`Initialize` creates an XrdSys socket, sets nonblocking flags, configures `TCP_NODELAY`, and installs platform SIGPIPE protection. `Connect` resolves host addresses and calls `ConnectToAddress`; timeout zero plus `EINPROGRESS` marks the socket `Connecting`, while successful synchronous connect marks it `Connected`. `ReadRaw`/`WriteRaw` loop until the requested size is transferred or timeout/error occurs, using `Poll` before `read`/`write`. Async-style `Send`, `Read`, and `ReadV` perform one syscall/TLS call and return `suRetry` for would-block cases. `Send(Message&)` advances the message cursor until fully written or retry/error.

## State And Persistence Behavior

The object stores file descriptor, connection status, server address, cached local/peer/name strings, protocol family, channel ID pointer, cork state, and optional TLS wrapper. `Close` shuts down TLS, closes the descriptor, clears cached names, and marks disconnected. State is process-local only.

## Dependencies And Integration Points

The implementation depends on `XrdClSocket.hh`, `Utils`, constants, `Message`, `DefaultEnv`, `Tls`, `XrdNetConnect`, `XrdSysFD`, POSIX sockets, `poll`, `fcntl`, `readv`, and TCP options. It is used by channel and transport code and interacts with `Poller` event mapping through `MapEvent`.

## Risks And Edge Cases

`ClassifyErrno(int error)` ignores its `error` parameter and switches on global `errno`, which is risky if callers pass a saved errno. `WriteRaw` uses plain `::write` instead of the SIGPIPE-safe `Send` helper. Timeout math uses `time(0)` seconds, so subsecond precision is unavailable and clock changes can affect waits. `Send(KernelBuffer)` is rejected over TLS. Name caching is mutable and not synchronized. Corking maps to `TCP_CORK` only where available and otherwise just updates the state flag.

## Test Signals

Tests should cover nonblocking initialization, async connect with `EINPROGRESS`, raw read/write success and timeout, would-block classification, remote close handling, message cursor reset on send error, TLS handshake success/failure, cork/flash behavior, and saved-errno classification correctness.
