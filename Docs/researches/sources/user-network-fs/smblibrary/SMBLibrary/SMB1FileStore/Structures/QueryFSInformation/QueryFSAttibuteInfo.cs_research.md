<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs

Purpose: Concrete SMB1 query-file-system information DTO for `SMB_QUERY_FS_ATTRIBUTE_INFO`.

Important APIs/types/functions: `QueryFSAttibuteInfo` provides a buffer constructor, `GetBytes`, `Length`, and `InformationLevel`; fixed portion is 12 bytes and contains file-system attributes, max component byte length, and UTF-16 file-system name.

Control flow: Parsing reads fixed fields and then any length-prefixed UTF-16 string. Serialization recomputes dynamic string byte lengths and writes a new byte array.

State and persistence behavior: State is the DTO fields only; no caching or persistence.

Dependencies and integration points: Used by `QueryFSInformation.GetQueryFSInformation` and `QueryFSInformationHelper` to bridge SMB1 FS queries to shared backend information.

Risks and edge cases: Buffer parsing trusts declared lengths. Volume label parsing appears to pass byte size as a UTF-16 character count, a likely boundary/overread risk for non-empty labels.

Test signals: Tests should cover empty and non-empty Unicode labels/names, numeric round trips, and truncated buffer rejection or documented failure modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs -->
