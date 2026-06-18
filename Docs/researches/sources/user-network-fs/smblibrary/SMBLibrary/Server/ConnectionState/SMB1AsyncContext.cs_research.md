# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1AsyncContext.cs

## Purpose

Carries context for a pending asynchronous SMB1 operation, mainly change-notify and cancel handling.

## Important APIs, Types, And Functions

Public fields hold UID, TID, PID, MID, FID, connection reference, and the backing file-store IO request token.

## Control Flow

Notify-change creates the context before calling the file store. Cancel lookup uses UID/TID/PID/MID to find it and passes `IORequest` to `Cancel`.

## State And Persistence Behavior

Connection-scoped in-memory pending request state in `SMB1ConnectionState.m_pendingRequests`.

## Dependencies And Integration Points

Used by `NotifyChangeHelper`, `CancelHelper`, and `SMB1ConnectionState`.

## Risks And Edge Cases

The untyped `IORequest` token must match the file-store implementation. Context identity omits command name, so reused MID/PID combinations must be managed carefully.

## Test Signals

Test pending notify creation, cancel removal, completion removal, and behavior after session or file closes before completion.

Source-read signal: reviewed the complete local source file for this item.
