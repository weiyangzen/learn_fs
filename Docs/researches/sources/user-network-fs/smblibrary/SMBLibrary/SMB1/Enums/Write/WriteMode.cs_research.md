# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Write/WriteMode.cs

- **Purpose:** Defines protocol constants for WriteMode. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 13 lines, 231 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteMode`.
- **Important APIs/types/functions:** Types: enum WriteMode : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: WritethroughMode=0x0001, ReadBytesAvailable=0x0002, RAW_MODE=0x0004, MSG_START=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
