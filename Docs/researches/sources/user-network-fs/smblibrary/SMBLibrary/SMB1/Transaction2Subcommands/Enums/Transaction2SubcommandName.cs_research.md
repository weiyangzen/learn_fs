# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Transaction2SubcommandName.cs

- **Purpose:** Defines protocol constants for Transaction2SubcommandName. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 18 lines, 560 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SubcommandName`.
- **Important APIs/types/functions:** Types: enum Transaction2SubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: TRANS2_OPEN2=0x0000, TRANS2_FIND_FIRST2=0x0001, TRANS2_FIND_NEXT2=0x0002, TRANS2_QUERY_FS_INFORMATION=0x0003, TRANS2_SET_FS_INFORMATION=0x0004, TRANS2_QUERY_PATH_INFORMATION=0x0005, TRANS2_SET_PATH_INFORMATION=0x006, TRANS2_QUERY_FILE_INFORMATION=0x0007, TRANS2_SET_FILE_INFORMATION=0x0008, TRANS2_CREATE_DIRECTORY=0x000D, TRANS2_GET_DFS_REFERRAL=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
