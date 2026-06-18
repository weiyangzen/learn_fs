<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs

## Purpose
NDR structure for MS-WKST `WKSTA_INFO_100`, carrying platform, computer name, LAN group, and version.

## APIs, Types, and Functions
Fields are `PlatformID`, `ComputerName`, `LanGroup`, `VerMajor`, and `VerMinor`. Implements parser constructor, `Read()`, `Write()`, and `Level => 100`.

## Control Flow, State, and Persistence
Constructor initializes string fields. Read/write use embedded full pointers for strings and scalar version fields. No persistence.

## Dependencies and Integration
Used by `WorkstationService` level-100 responses.

## Risks and Test Signals
Risks include hard-coded version data and null strings in uninitialized instances. Test NDR round trips and Windows workstation info client behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs -->
