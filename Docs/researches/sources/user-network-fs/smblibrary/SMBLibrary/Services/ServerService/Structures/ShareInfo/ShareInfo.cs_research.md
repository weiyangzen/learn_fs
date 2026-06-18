<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs

## Purpose
NDR union wrapper for single-share information responses.

## APIs, Types, and Functions
Fields are `uint Level` and `IShareInfoEntry Info`. Constructors support empty, level-only, concrete entry, and parser forms. `Read()` and `Write()` serialize the union.

## Control Flow, State, and Persistence
`Read()` currently recognizes levels 100 and 101 and maps them to `ShareInfo0Entry` and `ShareInfo1Entry`; other levels throw `InvalidLevelException`. `Write()` writes the level and embedded entry pointer. No persistence.

## Dependencies and Integration
Used by `NetrShareGetInfoResponse` and `ServerService`.

## Risks and Test Signals
Important risk: the parser appears inconsistent with service levels 0/1/2 and MS-SRVS share info levels, so round-trip parsing of this library's own level-0/1/2 responses may fail. Test Windows client unmarshalling and local parse/serialize for all supported service levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs -->
