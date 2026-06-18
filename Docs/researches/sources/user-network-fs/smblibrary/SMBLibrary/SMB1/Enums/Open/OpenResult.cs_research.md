# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenResult.cs

- **Purpose:** Defines protocol constants for OpenResult. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 225 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenResult`.
- **Important APIs/types/functions:** Types: enum OpenResult : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: Reserved=0x00, FileExistedAndWasOpened=0x01, NotExistedAndWasCreated=0x02, FileExistedAndWasTruncated=0x03.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
