<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs

## Purpose
NDR response model for MS-WKST `NetrWkstaGetInfo`.

## APIs, Types, and Functions
Fields are `WorkstationInfo WkstaInfo` and `Win32Error Result`; constructors support empty and parsed forms; `GetBytes()` writes the info union and result.

## Control Flow, State, and Persistence
Parsing reads `WorkstationInfo` then a trailing result. Writing emits the same order. No persistence.

## Dependencies and Integration
Produced by `WorkstationService.GetNetrWkstaGetInfoResponse()`.

## Risks and Test Signals
Risks include null `WkstaInfo` serialization and parser throwing for unsupported levels. Test success levels 100/101 and unsupported/invalid responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs -->
