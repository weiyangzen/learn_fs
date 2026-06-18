<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs

## Purpose
NDR request model for MS-SRVS `NetrShareGetInfo`.

## APIs, Types, and Functions
Fields are `ServerName`, `NetName`, and `Level`. The byte constructor parses those fields; `GetBytes()` serializes them.

## Control Flow, State, and Persistence
Parsing reads a top-level Unicode server-name pointer, an inline Unicode share name, and the requested info level. No validation or persistence.

## Dependencies and Integration
Used by `ServerService.GetResponseBytes()` for opnum 16 and by `GetNetrShareGetInfoResponse()`.

## Risks and Test Signals
Risks include no null/empty share-name validation and no default constructor despite response classes having one. Test case-insensitive share lookup, missing shares, and level 0/1/2/unsupported/invalid requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs -->
