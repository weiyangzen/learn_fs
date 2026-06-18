# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/FindInformationLevel.cs

- **Purpose:** Defines protocol constants for FindInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 16 lines, 618 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FindInformationLevel`.
- **Important APIs/types/functions:** Types: enum FindInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_STANDARD=0x0001, SMB_INFO_QUERY_EA_SIZE=0x0002, SMB_INFO_QUERY_EAS_FROM_LIST=0x0003, SMB_FIND_FILE_DIRECTORY_INFO=0x0101, SMB_FIND_FILE_FULL_DIRECTORY_INFO=0x0102, SMB_FIND_FILE_NAMES_INFO=0x0103, SMB_FIND_FILE_BOTH_DIRECTORY_INFO=0x0104, SMB_FIND_FILE_ID_FULL_DIRECTORY_INFO=0x0105, SMB_FIND_FILE_ID_BOTH_DIRECTORY_INFO=0x0106.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
