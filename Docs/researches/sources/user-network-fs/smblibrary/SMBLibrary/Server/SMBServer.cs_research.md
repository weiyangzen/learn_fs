<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs

## Purpose
Core SMB server transport and connection lifecycle. It listens on NetBIOS-over-TCP or Direct TCP, accepts sockets, receives NetBIOS session packets, detects SMB1 versus SMB2 payloads, dispatches protocol handlers, sends queued responses, manages keepalive/inactivity behavior, and exposes session information.

## APIs, Types, and Functions
Public API includes constructor, `Start()` overloads, `Stop()`, `GetSessionsInformation()`, `TerminateConnection()`, and events `ConnectionRequested` and `LogEntryAdded`. Internal callbacks include `ConnectRequestCallback()`, `ReceiveCallback()`, `ProcessConnectionBuffer()`, `ProcessPacket()`, `ProcessSendQueue()`, and `Log()`.

## Control Flow, State, and Persistence
`Start()` binds/listens, records enabled dialects, and optionally starts an inactivity keepalive thread. Accept creates `ConnectionState`, applies TCP keepalive and no-delay, lets subscribers reject clients, starts a send thread, and begins async receive. Receive buffers are locked while packets are dequeued and dispatched. SMB1 negotiate can upgrade to SMB2 when SMB2 dialect strings are present. `Stop()` stops listening, cancels keepalive, releases sockets, and releases all connections. State is in fields for shares, security provider, named-pipe services, server GUID, connection manager, listener socket, dialect flags, and start time.

## Dependencies and Integration
This partial class is extended by SMB1/SMB2 dispatch files. It depends on sockets, NetBIOS packet classes, connection state classes, `SMBShareCollection`, `NamedPipeShare`, `GSSProvider`, `SocketUtils`, and logging.

## Risks and Test Signals
Risks include async callback races during shutdown, connection-state replacement while receive callback continues, per-connection send threads, listener accept errors that may stop accepting for non-reset errors, and large packet handling tied to negotiate paths. Test start/stop idempotence, connection rejection, SMB1-disabled upgrade behavior, DirectTCP and NetBIOS packets, invalid packets closing sockets, keepalive thread cancellation, and concurrent clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs -->
