# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ResourceType.cs

- **Purpose:** OpenAndX Response: Valid. OpenAndX Extended Response: Invalid (SMB 1.0). NTCreateAndX Response: Valid. NTCreateAndX Extended Response: Invalid (SMB 1.0). Transact2Open2: Was never valid. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 28 lines, 810 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ResourceType`.
- **Important APIs/types/functions:** Types: enum ResourceType : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: FileTypeDisk=0x0000, FileTypeByteModePipe=0x0001, FileTypeMessageModePipe=0x0002, FileTypePrinter=0x0003, FileTypeCommDevice=0x0004, FileTypeUnknown=0xFFFF.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
