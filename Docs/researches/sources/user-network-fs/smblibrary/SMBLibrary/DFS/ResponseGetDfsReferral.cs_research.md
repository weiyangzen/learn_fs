<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs

## Purpose
Represents `RESP_GET_DFS_REFERRAL`, the DFS response header and ordered list of versioned referral entries.

## Important APIs, Types, And Functions
Direct types: ResponseGetDfsReferral class. Fields include HeaderSize:int, MinReferralEntryHeaderSize:int, PathConsumed:ushort, ReferralHeaderFlags:DfsReferralHeaderFlags, ReferralEntries:List<DfsReferralEntry>. Direct methods: ResponseGetDfsReferral, GetBytes.

## Control Flow
Parsing reads `PathConsumed`, referral count, header flags, then loops through `DfsReferralEntry.ReadEntry` while validating that entry headers fit. Serialization computes fixed-entry length first, then trailing string area, writes the header, and asks each entry to serialize itself with the current string offset.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs -->
