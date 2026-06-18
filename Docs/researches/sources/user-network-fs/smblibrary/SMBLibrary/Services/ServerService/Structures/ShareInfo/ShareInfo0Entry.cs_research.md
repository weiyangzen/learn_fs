<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_0`, containing only the share name.

## APIs, Types, and Functions
Field `NDRUnicodeString NetName`; constructors for empty, share-name, and parser; methods `Read()`, `Write()`, and `Level => 0`.

## Control Flow, State, and Persistence
Read/write wrap a structure and use an embedded full pointer for `NetName`. No persistence.

## Dependencies and Integration
Used by level-0 share enum/get-info responses.

## Risks and Test Signals
Risks include null `NetName` in empty instances and pointer serialization correctness. Test share names with case, spaces, and empty/null scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs -->
