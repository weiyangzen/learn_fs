<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs

## Purpose
NDR response model for MS-SRVS `NetrShareGetInfo`.

## APIs, Types, and Functions
Fields are `ShareInfo InfoStruct` and `Win32Error Result`. The class supports empty construction, parsing, and `GetBytes()` serialization.

## Control Flow, State, and Persistence
Parsing reads the share-info union followed by the result code. Writing emits the union then result. No persistence.

## Dependencies and Integration
Produced by `ServerService.GetNetrShareGetInfoResponse()`.

## Risks and Test Signals
Risks include null info structs and a `ShareInfo` parser that recognizes levels 100/101 even though service writes 0/1/2, making round-trip parsing suspect. Test serialized responses with Windows clients for each supported level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs -->
