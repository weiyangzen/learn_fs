# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2AsyncContext.cs

## Purpose

Carries context for a pending asynchronous SMB2 operation.

## Important APIs, Types, And Functions

Public fields hold async id, `FileID`, connection, session id, tree id, and file-store IO request token.

## Control Flow

Created by `SMB2ConnectionState.CreateAsyncContext`, later looked up by async id for completion or cancellation.

## State And Persistence Behavior

Connection-scoped pending request state in an SMB2 async dictionary.

## Dependencies And Integration Points

Uses `SMB2.FileID` and `SMB2ConnectionState`.

## Risks And Edge Cases

The class is an unvalidated bag of fields. Callers must ensure session/tree/file are still valid when the async completion arrives.

## Test Signals

Test async id creation, lookup, removal, cancellation, and completion after file/session close.

Source-read signal: reviewed the complete local source file for this item.
