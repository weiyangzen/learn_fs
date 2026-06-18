<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs

## Purpose
Enumerates MS-WKST workstation-service RPC operation numbers.

## APIs, Types, and Functions
`WorkstationServiceOpName : ushort` maps opnums including `NetrWkstaGetInfo = 0` and many unsupported workstation, use, join, and computer-name operations.

## Control Flow, State, and Persistence
No logic. `WorkstationService.GetResponseBytes()` switches on this enum and implements only get-info.

## Dependencies and Integration
Used by `WorkstationService` dispatch and RPC unsupported-op fault handling.

## Risks and Test Signals
Risk is limited to enum members implying support that is not implemented. Test opnum 0 success and unsupported opnums producing op-range faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs -->
