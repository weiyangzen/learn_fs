<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_1`, carrying share name, type, and remark.

## APIs, Types, and Functions
Fields are `NetName`, `ShareType`, and `Remark`. Constructors create empty, share-name/type, or parsed entries. Implements `Read()`, `Write()`, and `Level => 1`.

## Control Flow, State, and Persistence
Share-name constructor initializes an empty remark. Read/write use embedded string pointers and `ShareTypeExtended` serialization. No persistence.

## Dependencies and Integration
Used by level-1 share enum/get-info responses.

## Risks and Test Signals
Risks include empty instances with null strings and hard-coded empty remarks in service responses. Test serialization for disk and special shares, empty remarks, and Unicode share names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs -->
