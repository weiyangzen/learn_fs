<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs

Purpose: Abstract base and factory for SMB1 query-file-system information payloads.

Important APIs/types/functions: Defines abstract `GetBytes(bool isUnicode)`, `Length`, `InformationLevel`, and static `GetQueryFSInformation`.

Control flow: Factory switches on `QueryFSInformationLevel` and constructs the matching concrete class from buffer offset zero.

State and persistence behavior: No state beyond subclass data.

Dependencies and integration points: Integrated by SMB1 query FS transaction handling and `QueryFSInformationHelper` conversions.

Risks and edge cases: The `isUnicode` parameter is not used by current concrete FS info classes because these structures use Unicode strings by specification. Unsupported levels throw.

Test signals: Tests should verify factory dispatch and unsupported-level exception paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs -->
