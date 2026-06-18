<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs

Purpose: Abstract base and factory for SMB1 query-file information records.

Important APIs/types/functions: Defines abstract `GetBytes`, `InformationLevel`, and static `GetQueryInformation` covering basic, standard, EA, name, all, alternate-name, stream, and compression classes.

Control flow: Factory switches on `QueryInformationLevel` and constructs concrete DTOs at offset zero.

State and persistence behavior: No internal state beyond subclass payloads.

Dependencies and integration points: Central parser entry for SMB1 query file/path information responses and helper conversion logic.

Risks and edge cases: Unsupported levels throw. The factory does not pre-check buffer length, so malformed inputs surface from concrete constructors.

Test signals: Tests should exercise every supported dispatch branch and unsupported-level behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs -->
