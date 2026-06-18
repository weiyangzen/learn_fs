<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V1`, an older referral entry containing a server type, flags, and inline UTF-16 share name.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV1 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, ShareName:string. Direct methods: DfsReferralEntryV1, WriteBytes.

## Control Flow
The constructor reads fixed header fields and a null-terminated share name at offset 8. `WriteBytes` writes the header plus inline share name and reports a total length of fixed bytes plus the UTF-16 terminator.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs -->
