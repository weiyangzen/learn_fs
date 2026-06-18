<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs

Purpose: Represents the [MS-CIFS] SMB_FEA_LIST collection used by SMB1 extended attribute query/set payloads.

Important APIs/types/functions: Public API is the `FullExtendedAttributeList` constructor(s), `WriteBytes`, `GetBytes` where present, and `Length`; the record details are 32-bit total length and repeated `FullExtendedAttribute` entries with an overload that advances a ref offset.

Control flow: Parsing reads fields sequentially from a caller-provided buffer offset. Serialization recomputes length fields from current string/list contents and writes little-endian or ANSI bytes.

State and persistence behavior: The object stores only in-memory attribute names, values, flags, and list membership. There is no external persistence or caching.

Dependencies and integration points: Depends on `Utilities` byte readers/writers and SMB1 extended-attribute enums. Integrated into SMB1 transaction payloads that request or provide EA lists.

Risks and edge cases: Buffer constructors trust length fields and do not validate EOF, null terminators, string byte length overflow, or malformed list progress; non-ASCII ANSI conversion can also be lossy.

Test signals: Tests should include empty and multiple-entry lists, ANSI names/values, length-field round trips, ref-offset advancement for FEA lists, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs -->
