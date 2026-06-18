<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs

## Purpose
`RequestGetDfsReferralExTests.cs` validates parsing and serialization round-trip behavior for DFS referral extended requests with a site-name payload.

## Important APIs, Types, And Functions
The tests exercise `SMBLibrary.DFS.RequestGetDfsReferralEx`, `RequestGetDfsReferralExFlags.SiteName`, its byte constructor, properties `MaxReferralLevel`, `Flags`, `RequestFileName`, `SiteName`, and `GetBytes`.

## Control Flow
The parse test feeds a fixed little-endian/UTF-16LE byte buffer and asserts decoded referral level, flag, UNC request path, and site name. The round-trip test constructs an object with equivalent values, serializes it, reparses it, and asserts the same fields.

## State And Persistence
All data is in-memory. The fixed buffer acts as a protocol fixture.

## Dependencies And Integration Points
The tests depend on the DFS request parser/serializer and MSTest. The covered object is used by DFS management/request handling code that exchanges `FSCTL_DFS_GET_REFERRALS_EX`-style payloads.

## Risks
Coverage is limited to the SiteName flag and one well-formed request. It does not cover absent site names, invalid offsets/lengths, other flags, maximum referral levels, or malformed UTF-16 data.

## Test Signals
Good signal for normal site-name request decoding and object serialization preserving fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs -->
