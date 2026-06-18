<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs

## Purpose
`NetBiosTests.cs` validates NetBIOS name decoding and re-encoding round trips for two encoded name fixtures.

## Important APIs, Types, And Functions
The tests use `NetBiosUtils.DecodeName(buffer, ref offset)` and `NetBiosUtils.EncodeName(name, String.Empty)`, comparing byte arrays with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test decodes an encoded name from offset zero, then re-encodes the decoded name with an empty scope and asserts the original encoded bytes are reproduced.

## State And Persistence
All test data is in-memory protocol bytes.

## Dependencies And Integration Points
It depends on `SMBLibrary.NetBios` and `Utilities`. NetBIOS name utilities are relevant to legacy SMB/NetBIOS transport and name service handling.

## Risks
Only two simple fixtures are covered. The tests do not assert decoded text, offset advancement, scope handling, malformed names, or compression/pointer behavior.

## Test Signals
Basic signal for canonical NetBIOS 32-byte name encoding round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs -->
