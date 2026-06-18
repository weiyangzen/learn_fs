<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs

## Purpose
NDR model for the MS-SRVS `NetrServerGetInfo` request.

## APIs, Types, and Functions
Fields are `ServerName` and `Level`. Constructors support empty creation and parsing from a byte buffer. `GetBytes()` serializes the top-level Unicode string pointer and level.

## Control Flow, State, and Persistence
Parsing constructs an `NDRParser`, reads the server-name pointer, then the info level. Serialization mirrors that order with `NDRWriter`. No persistence.

## Dependencies and Integration
Used by `ServerService.GetResponseBytes()` for opnum 21.

## Risks and Test Signals
Risks include no validation of server name or trailing bytes. Test parse/serialize round trips for null and non-null server names and supported/unsupported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs -->
