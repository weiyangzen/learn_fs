<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs

## Purpose
NDR structure for MS-SRVS `SERVER_INFO_101`, adding version, server type flags, and comment to level-100 data.

## APIs, Types, and Functions
Fields are `PlatformID`, `ServerName`, `VerMajor`, `VerMinor`, `ServerType Type`, and `NDRUnicodeString Comment`. It implements `Read()`, `Write()`, and `Level => 101`.

## Control Flow, State, and Persistence
Read/write use NDR structure boundaries and embedded full pointers for strings. Constructor initializes `ServerName` and `Comment`. No persistence.

## Dependencies and Integration
Used by `ServerService` level-101 server info responses.

## Risks and Test Signals
Risks include hard-coded version/type data from service construction and null string fields if not initialized. Test level-101 response unmarshalling, type-flag combinations, and empty comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs -->
