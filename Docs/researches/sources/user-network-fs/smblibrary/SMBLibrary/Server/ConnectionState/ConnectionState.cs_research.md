# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ConnectionState.cs

## Purpose

Base connection state shared by SMB1 and SMB2 connections. It holds socket, endpoint, NetBIOS receive buffer, send queue, timestamps, dialect, authentication context, and logging callback.

## Important APIs, Types, And Functions

Constructors create or wrap state; virtual `CloseSessions` and `GetSessionsInformation` are overridden by dialect-specific subclasses. Properties expose transport objects and timestamps; `UpdateLastReceiveDT`, `UpdateLastSendDT`, and `ConnectionIdentifier` support connection management.

## Control Flow

The copy constructor preserves the same socket, receive buffer, send queue, and last-send reference when upgrading a generic state into SMB1 or SMB2 state. Logging prefixes messages with endpoint identity.

## State And Persistence Behavior

Connection-scoped in-memory state. `LastSendDTRef` is deliberately shared so sender threads keep updating the original reference after state conversion.

## Dependencies And Integration Points

Depends on sockets, NetBIOS `SessionPacket`, `NBTConnectionReceiveBuffer`, GSS authentication context, and `Utilities.BlockingQueue`/`Reference`.

## Risks And Edge Cases

Most fields are not synchronized beyond the send timestamp reference. Subclasses must close sessions to avoid leaking file handles. `AuthenticationContext` is not copied in the copy constructor, so callers must understand when it is transferred or reused.

## Test Signals

Test SMB1/SMB2 state conversion, timestamp updates visible through the shared reference, connection identifier formatting, and subclass close/session-info overrides.

Source-read signal: reviewed the complete local source file for this item.
