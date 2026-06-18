<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs

## Purpose
Models DFS referral V4 as a V3-compatible entry with target-set boundary flag support.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV4 class. Fields include none declared. Direct methods: DfsReferralEntryV4.

## Control Flow
The class inherits V3 parsing/writing and sets `VersionNumber = 4`; `IsTargetSetBoundary` exposes the V4-specific flag as a boolean property over `ReferralEntryFlags`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs -->
