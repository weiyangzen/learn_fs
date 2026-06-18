<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V2`, with proximity, TTL, DFS path, alternate path, and target network address.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV2 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, Proximity:uint, TimeToLive:uint, DfsPath:string, DfsAlternatePath:string, NetworkAddress:string. Direct methods: DfsReferralEntryV2, WriteBytes.

## Control Flow
The constructor reads fixed fields and three offsets relative to the entry start, then decodes referenced UTF-16 strings. `WriteBytes` lays the fixed entry first, writes relative string offsets, then writes the three null-terminated strings into the shared trailing string area.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs -->
