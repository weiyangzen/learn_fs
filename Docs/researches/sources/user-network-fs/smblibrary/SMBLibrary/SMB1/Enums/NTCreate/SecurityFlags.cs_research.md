# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/SecurityFlags.cs

- **Purpose:** Defines protocol constants for SecurityFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 10 lines, 184 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SecurityFlags`.
- **Important APIs/types/functions:** Types: enum SecurityFlags : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_SECURITY_CONTEXT_TRACKING=0x01, SMB_SECURITY_EFFECTIVE_ONLY=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
