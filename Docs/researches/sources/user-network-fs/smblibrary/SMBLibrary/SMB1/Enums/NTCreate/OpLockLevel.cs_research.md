# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/OpLockLevel.cs

- **Purpose:** Defines protocol constants for OpLockLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 220 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpLockLevel`.
- **Important APIs/types/functions:** Types: enum OpLockLevel : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NoOpLockGranted=0x00, ExclusiveOpLockGranted=0x01, BatchOpLockGranted=0x02, Level2OpLockGranted=0x03.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
