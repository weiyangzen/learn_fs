<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs

## Purpose
`NegotiateResponseParsingTests.cs` validates SMB 3.1.1 negotiate response parsing with negotiate context lists, non-zero offsets, and serialization round trip.

## Important APIs, Types, And Functions
The class exercises `SMBLibrary.SMB2.NegotiateResponse`, `DialectRevision`, `SMB2Dialect.SMB311`, `NegotiateContextList`, and `GetBytes`.

## Control Flow
A large fixture containing an SMB2 negotiate response and two negotiate contexts is parsed at offset zero and offset two. A third test serializes the parsed object, reparses it, and verifies the dialect and context count remain intact.

## State And Persistence
All test state is in-memory protocol bytes.

## Dependencies And Integration Points
It depends on SMB2 negotiate response parsing and is relevant to SMB 3.1.1 session setup because negotiated dialect and contexts feed preauth, encryption, signing, and capabilities.

## Risks
The tests do not assert individual context payload contents, security buffer details, timestamps, GUIDs, or capability flags. Malformed padding and truncated context lists are not covered.

## Test Signals
Good signal for response context-list offset handling and serializer preservation for SMB 3.1.1 negotiate responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs -->
