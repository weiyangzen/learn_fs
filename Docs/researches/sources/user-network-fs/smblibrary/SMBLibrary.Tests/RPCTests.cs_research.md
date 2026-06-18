<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs

## Purpose
`RPCTests.cs` validates parsing of selected SRVSVC/WKSSVC RPC request and response structures from fixed NDR byte fixtures.

## Important APIs, Types, And Functions
The tests instantiate `NetrWkstaGetInfoResponse`, `NetrServerGetInfoResponse`, `NetrShareEnumRequest`, `NetrShareEnumResponse`, and `NetrShareGetInfoRequest`. They inspect `WorkstationInfo100`, `ServerInfo101`, `ShareInfo1Container`, info levels, counts, server names, share names, and total entries.

## Control Flow
Each test feeds a static byte buffer to the relevant RPC model constructor, then asserts decoded discriminated-union level, concrete info type, string values, and counts.

## State And Persistence
The file uses only in-memory protocol fixtures.

## Dependencies And Integration Points
It depends on `SMBLibrary.Services` RPC model types. These structures integrate with named pipe RPC services exposed over SMB, especially workstation and server service calls.

## Risks
Coverage is parser-only for selected well-formed little-endian NDR fixtures. Serialization, malformed buffers, alignment edge cases, different info levels, and non-ASCII strings are not covered.

## Test Signals
Useful signal for NDR pointer/string/count decoding in common workstation, server, and share RPC paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs -->
