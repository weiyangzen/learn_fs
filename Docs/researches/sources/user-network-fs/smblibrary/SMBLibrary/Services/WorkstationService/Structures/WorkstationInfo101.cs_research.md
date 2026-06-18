<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs

## Purpose
NDR structure for MS-WKST `WKSTA_INFO_101`, adding LAN root to level-100 workstation information.

## APIs, Types, and Functions
Fields are `PlatformID`, `ComputerName`, `LanGroup`, `VerMajor`, `VerMinor`, and `LanRoot`. Implements `Read()`, `Write()`, and `Level => 101`.

## Control Flow, State, and Persistence
Constructor initializes all string fields. Read/write use NDR embedded full pointers. No persistence.

## Dependencies and Integration
Used by `WorkstationService` level-101 responses.

## Risks and Test Signals
Risks include `LanRoot` set to LAN group by the service, which may not match client expectations, and hard-coded version identity. Test level-101 NDR serialization and client display.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs -->
