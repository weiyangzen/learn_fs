# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/AccessRights.cs

- **Purpose:** Defines protocol constants for AccessRights. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 10 lines, 193 bytes. Namespace `SMBLibrary.SMB1`. Primary type `AccessRights`.
- **Important APIs/types/functions:** Types: enum AccessRights : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_DA_ACCESS_READ=0x00, SMB_DA_ACCESS_WRITE=0x01, SMB_DA_ACCESS_READ_WRITE=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
