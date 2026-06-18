<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs

Purpose: Concrete SMB1 set-information request payload for `SMB_SET_FILE_ALLOCATION_INFO`.

Important APIs/types/functions: `SetFileAllocationInfo` provides default and buffer constructors, `GetBytes`, and `InformationLevel`; it carries allocation size as an Int64 byte length.

Control flow: Parsing reads the fixed-size little-endian structure. Serialization emits the fixed-size request body from current field values.

State and persistence behavior: State is the requested mutation values only; persistence happens later in the file-store backend after helper conversion.

Dependencies and integration points: Used by `SetInformation.GetSetInformation` and `SetInformationHelper` to convert SMB1 set requests into shared `FileInformation` mutation DTOs.

Risks and edge cases: Constructors trust buffer length. Time-setting semantics depend on `SetFileTime` sentinel handling, and size fields require backend validation for negative or unsupported truncation/extension values.

Test signals: Tests should cover fixed lengths, boolean encoding, set-time sentinel values, negative and large sizes, and helper conversion into shared classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs -->
