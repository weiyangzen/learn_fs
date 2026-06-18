# sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/SessionInformation.cs

## Purpose

DTO for reporting an authenticated SMB session and its open files.

## Important APIs, Types, And Functions

Public fields are client endpoint, dialect, user name, machine name, open file list, and creation timestamp. The constructor initializes all fields.

## Control Flow

No internal logic; connection states aggregate instances from sessions.

## State And Persistence Behavior

Snapshot of in-memory session state.

## Dependencies And Integration Points

Uses `OpenFileInformation`, `SMBDialect`, and `IPEndPoint`.

## Risks And Edge Cases

Mutable fields and lists can be altered by consumers unless copied. The open-file list can be stale under concurrent close/open activity.

## Test Signals

Test aggregation across multiple SMB1/SMB2 sessions and snapshot contents after file open and close.

Source-read signal: reviewed the complete local source file for this item.
