<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs

Purpose: List wrapper for parsing and serializing chained SMB1 find-information entries.

Important APIs/types/functions: Constructors parse a buffer into entries; `GetBytes` assigns `NextEntryOffset` for all but the final entry; `GetLength` sums serialized lengths.

Control flow: Parsing follows each entry’s `NextEntryOffset` until zero. Serialization first updates offsets, then writes entries sequentially.

State and persistence behavior: Mutates contained entries by setting `NextEntryOffset`; otherwise state is the list contents only.

Dependencies and integration points: Depends on `FindInformation.ReadEntry` and concrete entry length calculations. Used by directory enumeration responses and parsers.

Risks and edge cases: A malformed non-advancing or out-of-range `NextEntryOffset` can break parsing. Serialization does not 8-byte-align entries, so it relies on each SMB1 structure’s expected length behavior.

Test signals: Tests should cover one-entry and multi-entry buffers, final zero offset, malformed offsets, Unicode/OEM lengths, and page-size truncation via `FindInformationHelper`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs -->
