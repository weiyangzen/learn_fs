<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs

## Purpose
Flags enum for MS-SRVS server software type values advertised in server information responses.

## APIs, Types, and Functions
`ServerType : uint` includes workstation, server, domain roles, browser roles, NT/windows flags, terminal/cluster flags, local-list-only, primary-domain, and `All`.

## Control Flow, State, and Persistence
No logic. `ServerService` combines selected flags for level-101 server info.

## Dependencies and Integration
Used by `ServerInfo101` and `ServerService`.

## Risks and Test Signals
Risks include duplicate/ambiguous cluster comments and service identity that may not reflect deployment role. Test level-101 serialization and client interpretation of advertised type flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs -->
