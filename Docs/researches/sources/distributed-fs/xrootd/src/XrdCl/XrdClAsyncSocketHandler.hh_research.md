# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.hh

Purpose: declares `AsyncSocketHandler`, the `SocketHandler` implementation used by XrdCl streams for asynchronous network I/O.

Important APIs/types: constructors, `SetAddress`, `GetAddress`, `Connect`, `PreClose`, `Close`, `Event`, `EnableUplink`, `DisableUplink`, stream/address getters, and protected event/handshake/fault/TLS helpers. State members include poller, transport, channel data, substream, stream name, socket, handshake data, timeout fields, TLS/reset flags, async reader/writer objects, and channel lifetime guard.

Control flow/state: the interface models a two-phase lifecycle: connecting/handshaking, then normal request/response I/O. It exposes only the operational entry points to callers while keeping the protocol state machine protected. Dependencies are XrdCl socket/poller/transport/task/URL/async reader-writer headers and compiler annotations. Risks: copy constructor recreates a handler around shared raw dependencies, event callbacks can trigger stream deletion, and uplink notification errors are fatal. Test signals: state transition coverage, copy construction behavior, poller notification failures, and helper address formatting.
