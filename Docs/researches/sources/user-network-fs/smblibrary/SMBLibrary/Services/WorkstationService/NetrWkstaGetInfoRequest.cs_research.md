<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs

## Purpose
NDR request model for MS-WKST `NetrWkstaGetInfo`.

## APIs, Types, and Functions
Fields are `ServerName` and `Level`; constructors support empty and byte parsing; `GetBytes()` serializes the top-level Unicode string pointer and level.

## Control Flow, State, and Persistence
Parsing and writing are straightforward NDR operations. No validation or persistence.

## Dependencies and Integration
Used by `WorkstationService.GetResponseBytes()` for opnum 0.

## Risks and Test Signals
Risks include no server-name validation and unchecked malformed buffers. Test parse/serialize round trips for levels 100, 101, unsupported, and invalid values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs -->
