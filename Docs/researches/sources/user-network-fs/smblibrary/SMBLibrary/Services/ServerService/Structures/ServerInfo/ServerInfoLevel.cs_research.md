<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs

## Purpose
Abstract base for concrete server-info NDR structures.

## APIs, Types, and Functions
Declares abstract `Read(NDRParser)`, `Write(NDRWriter)`, and `uint Level`.

## Control Flow, State, and Persistence
No implementation state. Concrete subclasses implement NDR serialization for specific levels.

## Dependencies and Integration
Used by `ServerInfo` union and `ServerInfo100/101`.

## Risks and Test Signals
Risk is low; level consistency is enforced by caller conventions rather than this base. Test each concrete subclass through `ServerInfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs -->
