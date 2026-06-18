<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_2`, extending share info with permissions, use counts, path, and password.

## APIs, Types, and Functions
Fields include `NetName`, `ShareType`, `Remark`, `Permissions`, `MaxUses`, `CurrentUses`, `Path`, and `Password`; constant `UnlimitedConnections`; constructors, `Read()`, `Write()`, and `Level => 2`.

## Control Flow, State, and Persistence
The share-name constructor sets empty remark/path, unlimited max uses, and null password. Read/write process strings as embedded full pointers and scalar fields in protocol order. No persistence.

## Dependencies and Integration
Used by `ServerService.GetNetrShareGetInfoResponse()` for level 2.

## Risks and Test Signals
Risks include service returning empty path rather than actual backing path, zero permissions, no current-use accounting, and nullable password pointer handling. Test level-2 get-info from Windows clients and local NDR serialization with null password.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs -->
