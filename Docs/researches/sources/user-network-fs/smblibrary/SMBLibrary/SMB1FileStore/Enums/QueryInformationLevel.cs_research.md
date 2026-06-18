# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryInformationLevel.cs

- **Purpose:** Defines protocol constants for QueryInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 20 lines, 749 bytes. Namespace `SMBLibrary.SMB1`. Primary type `QueryInformationLevel`.
- **Important APIs/types/functions:** Types: enum QueryInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_STANDARD=0x0001, SMB_INFO_QUERY_EA_SIZE=0x0002, SMB_INFO_QUERY_EAS_FROM_LIST=0x0003, SMB_INFO_QUERY_ALL_EAS=0x0004, SMB_INFO_IS_NAME_VALID=0x0006, SMB_QUERY_FILE_BASIC_INFO=0x0101, SMB_QUERY_FILE_STANDARD_INFO=0x0102, SMB_QUERY_FILE_EA_INFO=0x0103, SMB_QUERY_FILE_NAME_INFO=0x0104, SMB_QUERY_FILE_ALL_INFO=0x0107, SMB_QUERY_FILE_ALT_NAME_INFO=0x0108, SMB_QUERY_FILE_STREAM_INFO=0x0109, SMB_QUERY_FILE_COMPRESSION_INFO=0x010B.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
