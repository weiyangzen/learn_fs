<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs

## Purpose
NDR union wrapper for MS-SRVS `SERVER_INFO` levels.

## APIs, Types, and Functions
Fields are `uint Level` and `ServerInfoLevel Info`. Constructors support empty, level-only, concrete info, and parser forms. `Read()` handles levels 100 and 101; `Write()` emits the discriminant and embedded full pointer.

## Control Flow, State, and Persistence
`Read()` begins the union, reads the level, dispatches to `ServerInfo100` or `ServerInfo101`, and throws `InvalidLevelException` otherwise. `Write()` writes whatever `Info` pointer is present. No persistence.

## Dependencies and Integration
Used by server get-info responses and parsing. Depends on `NDRParser`, `NDRWriter`, and concrete server info structures.

## Risks and Test Signals
Risks include no level-vs-info validation in `Write()` and level-only unsupported responses writing null info pointers. Test level 100/101 round trips, invalid-level exceptions, and null-info response serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs -->
