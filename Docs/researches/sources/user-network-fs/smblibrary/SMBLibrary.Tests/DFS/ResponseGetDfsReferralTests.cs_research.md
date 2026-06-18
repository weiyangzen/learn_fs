<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs

## Purpose
`ResponseGetDfsReferralTests.cs` validates DFS referral response parsing for version 4 entries and one serialization round trip.

## Important APIs, Types, And Functions
The MSTest class exercises `ResponseGetDfsReferral`, `DfsReferralEntryV4`, `DfsReferralHeaderFlags`, `DfsReferralEntryFlags`, `ReferralEntries`, `PathConsumed`, `TimeToLive`, paths, network addresses, and `ServiceSiteGuid`.

## Control Flow
One test parses a Windows Server 2008 R2 single-entry fixture and checks header flags plus all V4 entry fields. Another parses a two-entry fixture and validates per-entry target boundaries and network addresses. The round-trip test builds a single V4 entry response, serializes with `GetBytes`, reparses, and revalidates.

## State And Persistence
All fixtures and result objects are in-memory protocol data. No persistent state is created.

## Dependencies And Integration Points
It depends on `SMBLibrary.DFS` response models and is relevant to DFS referral client/server handling.

## Risks
Tests cover V4 entries only and do not exercise V1/V2/V3 referrals, malformed offsets, inconsistent entry counts, non-empty service site GUIDs, or target-list ordering beyond fixed fixtures.

## Test Signals
Strong signal that common V4 DFS referral responses with one or more targets parse correctly and that basic V4 serialization is internally consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs -->
