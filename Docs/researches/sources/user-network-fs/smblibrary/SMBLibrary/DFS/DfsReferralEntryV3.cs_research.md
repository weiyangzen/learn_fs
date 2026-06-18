<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V3`, supporting normal referrals and NameListReferral entries used for SYSVOL/NETLOGON expansion.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV3 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, TimeToLive:uint, DfsPath:string, DfsAlternatePath:string, NetworkAddress:string, ServiceSiteGuid:Guid, SpecialName:string, ExpandedNames:List<string>. Direct methods: DfsReferralEntryV3, WriteBytes.

## Control Flow
Normal entries read offsets for DFS path, alternate path, network address, and service-site GUID. Name-list entries read special-name and expanded-name-list offsets. `WriteBytes`, `Length`, `StringsLength`, and `IsNameListReferral` switch behavior based on `NameListReferral`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs -->
