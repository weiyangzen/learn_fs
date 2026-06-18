<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs

## Purpose
Flags enum for legacy share permissions in server-service share info level 2.

## APIs, Types, and Functions
`Permissions : uint` defines read, write, create, execute, delete, attribute, and permission bits.

## Control Flow, State, and Persistence
No logic. `ShareInfo2Entry` serializes/deserializes the enum as a uint, and the sample responses leave it at zero.

## Dependencies and Integration
Integrated with `ShareInfo2Entry` and MS-SRVS-compatible NDR serialization.

## Risks and Test Signals
Risk is low, but current service responses do not derive permissions from actual share access policy. Test level-2 share info serialization and client handling of zero permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs -->
