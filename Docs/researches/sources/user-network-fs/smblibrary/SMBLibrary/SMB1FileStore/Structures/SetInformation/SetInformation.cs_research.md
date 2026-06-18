<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs

Purpose: Abstract base and factory for SMB1 set-information request payloads.

Important APIs/types/functions: Defines abstract `GetBytes`, `InformationLevel`, and static `GetSetInformation` for basic, disposition, allocation, and EOF levels.

Control flow: Factory switches on `SetInformationLevel` and constructs concrete fixed-layout DTOs.

State and persistence behavior: No state beyond subclass payloads.

Dependencies and integration points: Integration point for SMB1 transaction handlers before `SetInformationHelper` maps requests into backend file information classes.

Risks and edge cases: Unsupported levels throw. Buffer length is not checked before dispatch.

Test signals: Tests should cover all factory branches, unsupported-level exception behavior, and short-buffer handling expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs -->
