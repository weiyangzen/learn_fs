<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs

## Purpose
NDR model for `NetrServerGetInfo` responses, carrying a server-info union and Win32 result code.

## APIs, Types, and Functions
Fields are `ServerInfo InfoStruct` and `Win32Error Result`. Constructors parse from bytes or create empty responses. `GetBytes()` writes the structure and result.

## Control Flow, State, and Persistence
Parsing reads `ServerInfo` then the trailing result code. Writing serializes `InfoStruct` then result. No persistence.

## Dependencies and Integration
Produced by `ServerService.GetNetrWkstaGetInfoResponse()` despite the method name typo.

## Risks and Test Signals
Risks include null `InfoStruct` causing serialization failure and invalid-level parser exceptions if response bytes contain unsupported unions. Test level 100/101 success and unsupported/invalid levels carrying empty union pointers with correct Win32 codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs -->
