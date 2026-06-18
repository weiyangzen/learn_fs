<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs

## Purpose
NDR model for MS-SRVS `NetrShareEnum` requests.

## APIs, Types, and Functions
Fields are `ServerName`, `ShareEnum InfoStruct`, `PreferedMaximumLength`, and `ResumeHandle`. Constructors parse from bytes or create empty instances; `GetBytes()` serializes all fields.

## Control Flow, State, and Persistence
Parsing reads a top-level server-name pointer, embedded `ShareEnum`, preferred maximum length, and resume handle. The service currently ignores preferred length and resume handle when responding.

## Dependencies and Integration
Used by `ServerService.GetNetrShareEnumResponse()`.

## Risks and Test Signals
Risks include misspelled field name, no resume support, and exceptions for unsupported levels during `ShareEnum` parse. Test level 0/1 requests, unsupported levels, invalid levels, nonzero resume handle, and max-preferred-length behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs -->
