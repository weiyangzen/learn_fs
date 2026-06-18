# sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/OpenFileInformation.cs

## Purpose

DTO for reporting one open file in server session information.

## Important APIs, Types, And Functions

Public fields are share name, path, `FileAccess`, and open timestamp. The constructor initializes all fields.

## Control Flow

No logic; sessions build instances from `OpenFileObject` values.

## State And Persistence Behavior

Snapshot reporting state. It does not own or close the underlying file handle.

## Dependencies And Integration Points

Uses `System.IO.FileAccess`; consumed by `SessionInformation` and management/status APIs.

## Risks And Edge Cases

Fields are mutable and represent a point-in-time snapshot that can become stale immediately after reporting.

## Test Signals

Session information tests should assert open file entries match active handles and disappear after close or tree disconnect.

Source-read signal: reviewed the complete local source file for this item.
