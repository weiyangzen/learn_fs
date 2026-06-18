# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryFSInformationLevel.cs

- **Purpose:** Defines protocol constants for QueryFSInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 13 lines, 377 bytes. Namespace `SMBLibrary.SMB1`. Primary type `QueryFSInformationLevel`.
- **Important APIs/types/functions:** Types: enum QueryFSInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_ALLOCATION=0x0001, SMB_INFO_VOLUME=0x0002, SMB_QUERY_FS_VOLUME_INFO=0x0102, SMB_QUERY_FS_SIZE_INFO=0x0103, SMB_QUERY_FS_DEVICE_INFO=0x0104, SMB_QUERY_FS_ATTRIBUTE_INFO=0x0105.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
