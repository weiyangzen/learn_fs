<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs

## Purpose
Represents `REQ_GET_DFS_REFERRAL_EX`, adding flags, request file-name length, and optional site-name data to the basic DFS referral request.

## Important APIs, Types, And Functions
Direct types: RequestGetDfsReferralEx class. Fields include MaxReferralLevel:ushort, Flags:RequestGetDfsReferralExFlags, RequestFileName:string, SiteName:string. Direct methods: RequestGetDfsReferralEx, GetBytes.

## Control Flow
The byte constructor reads max referral level, flags, request-name length, request name, and optional null-terminated site name when the site flag is set. `GetBytes` mirrors that layout and includes a site-name terminator when present.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs -->
