<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs

## Purpose
`NegotiateRequestParsingTests.cs` validates SMB 3.1.1 negotiate request parsing when negotiate contexts are present and when the packet begins at non-zero buffer offsets.

## Important APIs, Types, And Functions
The tests exercise `SMBLibrary.SMB2.NegotiateRequest`, `NegotiateContextList`, `Dialects`, `NegotiateContextType.SMB2_PREAUTH_INTEGRITY_CAPABILITIES`, `SMB2_ENCRYPTION_CAPABILITIES`, and `GetBytes`.

## Control Flow
The fixture includes an SMB2 header, dialect list, and four negotiate contexts. Tests parse at offset zero, parse the same bytes copied two bytes into a larger buffer, and parse after a serialize/reparse cycle, asserting dialect count, context count, and first context types.

## State And Persistence
All state is in-memory byte fixture and parsed object state.

## Dependencies And Integration Points
It depends on SMB2 negotiate parser/serializer logic. The covered behavior is important for SMB 3.1.1 preauth integrity, encryption capabilities, compression, and signing or transport capabilities negotiation.

## Risks
Tests check counts and first context types but not all context payload fields. They do not cover malformed offsets, padding errors, missing contexts, or older dialect requests.

## Test Signals
Good regression signal for relative offset handling and preservation of negotiate context lists during serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs -->
