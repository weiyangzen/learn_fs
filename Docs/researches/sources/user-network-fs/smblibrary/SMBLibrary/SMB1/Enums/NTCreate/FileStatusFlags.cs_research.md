# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/FileStatusFlags.cs

- **Purpose:** Defines protocol constants for FileStatusFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 12 lines, 193 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FileStatusFlags`.
- **Important APIs/types/functions:** Types: enum FileStatusFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NO_EAS=0x01, NO_SUBSTREAMS=0x02, NO_REPARSETAG=0x04.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
