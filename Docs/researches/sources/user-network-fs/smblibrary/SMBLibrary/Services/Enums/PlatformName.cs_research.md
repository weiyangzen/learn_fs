<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs

## Purpose
Defines platform identifiers used by server and workstation RPC information structures.

## APIs, Types, and Functions
`PlatformName : uint` includes DOS, OS2, NT, OSF, and VMS numeric values matching MS-SRVS platform IDs.

## Control Flow, State, and Persistence
No runtime control flow or state. Values are serialized into NDR structures such as `ServerInfo100` and `ServerInfo101`.

## Dependencies and Integration
Used by `ServerService` and workstation/server info structures to advertise NT-compatible platform identity.

## Risks and Test Signals
Risk is limited to protocol value drift. Test NDR serialization of server/workstation info responses and client display of platform values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs -->
