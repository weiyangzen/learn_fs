# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionManager.cs

## Purpose

Tracks active server connections, releases connection resources, sends keepalive probes, and aggregates session information.

## Important APIs, Types, And Functions

`AddConnection`, `RemoveConnection`, `ReleaseConnection`, `ReleaseConnection(IPEndPoint)`, `SendSMBKeepAlive`, `ReleaseAllConnections`, and `GetSessionsInformation` operate on the active connection list.

## Control Flow

Connections are added under a list lock. Release aborts the send queue, releases the socket, closes sessions, disposes the receive buffer, and removes the entry. Keepalive snapshots the list and sends unsolicited SMB1 or SMB2 echo replies when both receive and send timestamps are stale.

## State And Persistence Behavior

Maintains in-memory `m_activeConnections`; no disk persistence. Releasing a connection cascades to session and file handle cleanup.

## Dependencies And Integration Points

Uses `ConnectionState`, SMB1/SMB2 echo helpers, `SMBServer.Enqueue*`, `SocketUtils`, and `SessionInformation`.

## Risks And Edge Cases

The keepalive snapshot is made without locking `m_activeConnections`, unlike other methods, so concurrent mutation could race. Release assumes buffer disposal under a receive-buffer lock is sufficient for any receiver thread.

## Test Signals

Exercise add/remove idempotence, release cleanup order, release by endpoint, keepalive for SMB1 and SMB2 states, and concurrent release while enumerating sessions.

Source-read signal: reviewed the complete local source file for this item.
