<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs

## Purpose
NDR model for MS-SRVS `NetrShareEnum` responses.

## APIs, Types, and Functions
Fields are `ShareEnum InfoStruct`, `TotalEntries`, `ResumeHandle`, and `Win32Error Result`. It can parse from bytes and serialize through `GetBytes()`.

## Control Flow, State, and Persistence
Read/write order is share enum structure, total entries, resume handle, result code. No persistent state.

## Dependencies and Integration
Created by `ServerService` share enumeration logic.

## Risks and Test Signals
Risks include null `InfoStruct`, resume handle not used for paging, and total entries always full share count. Test empty share list, level 0/1 arrays, unsupported/invalid-level responses, and client unmarshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs -->
