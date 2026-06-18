<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs

## Purpose
Enumerates MS-SRVS RPC operation numbers for the server service interface.

## APIs, Types, and Functions
`ServerServiceOpName : ushort` maps opnums such as `NetrShareEnum = 15`, `NetrShareGetInfo = 16`, and `NetrServerGetInfo = 21`, plus many unsupported operations.

## Control Flow, State, and Persistence
No logic. `ServerService.GetResponseBytes()` casts incoming opnums to this enum and switches on implemented values.

## Dependencies and Integration
Used by `ServerService` dispatch and RPC fault handling for unsupported operations.

## Risks and Test Signals
Risks include typos in rarely used names and false sense of support for enum members not implemented. Test implemented opnums return responses and unsupported enum values return RPC op-range faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs -->
