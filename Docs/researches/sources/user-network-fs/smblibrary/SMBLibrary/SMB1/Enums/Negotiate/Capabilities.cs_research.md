# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/Capabilities.cs

- **Purpose:** The server supports extended security for authentication. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 31 lines, 1272 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Capabilities`.
- **Important APIs/types/functions:** Types: enum Capabilities : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: RawMode=0x00000001, MPXMode=0x00000002, Unicode=0x00000004, LargeFiles=0x00000008, NTSMB=0x00000010, RpcRemoteApi=0x00000020, NTStatusCode=0x00000040, Level2Oplocks=0x00000080, LockAndRead=0x00000100, NTFind=0x00000200, DFS=0x00001000, InfoLevelPassthrough=0x00002000, LargeRead=0x00004000, LargeWrite=0x00008000, LightWeightIO=0x00010000, Unix=0x00800000, DynamicReauthentication=0x20000000, ExtendedSecurity=0x80000000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
