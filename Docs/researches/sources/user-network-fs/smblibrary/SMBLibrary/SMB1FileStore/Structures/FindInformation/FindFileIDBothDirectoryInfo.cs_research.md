<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_ID_BOTH_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileIDBothDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 104 bytes and carries both-directory metadata plus file id and reserved fields.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by ID both-directory responses.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs -->
