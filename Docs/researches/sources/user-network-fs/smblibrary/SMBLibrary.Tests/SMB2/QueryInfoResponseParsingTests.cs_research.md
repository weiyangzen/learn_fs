<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs

## Purpose
`QueryInfoResponseParsingTests.cs` validates extraction of security descriptor data from an SMB2 QUERY_INFO response.

## Important APIs, Types, And Functions
The test uses `SMBLibrary.SMB2.QueryInfoResponse`, `GetSecurityInformation`, `SecurityDescriptor`, `Dacl`, `AccessAllowedACE`, and `Sid.Revision`.

## Control Flow
It parses a fixed SMB2 query-info response fixture, extracts its security descriptor payload, then asserts the DACL contains two ACEs, the second is an access-allowed ACE, and that ACE's SID revision is one.

## State And Persistence
All data is in-memory protocol fixture state.

## Dependencies And Integration Points
It depends on SMB2 query-info response parsing and NT security descriptor/ACE parsing. This supports SMB clients querying file security metadata.

## Risks
The test checks only a few descriptor fields and one well-formed fixture. It does not cover owner/group/SACL parsing, offset/length validation, self-relative descriptor variants, malformed ACEs, or non-security query-info payloads.

## Test Signals
Focused signal that security-info response payload extraction and basic DACL/ACE decoding work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs -->
