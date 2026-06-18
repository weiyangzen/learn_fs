<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs

## Purpose
Represents the legacy `REQ_GET_DFS_REFERRAL` request payload with maximum referral level and requested UNC path.

## Important APIs, Types, And Functions
Direct types: RequestGetDfsReferral class. Fields include MaxReferralLevel:ushort, RequestFileName:string. Direct methods: RequestGetDfsReferral, GetBytes.

## Control Flow
The byte constructor reads `MaxReferralLevel` and then decodes the remaining UTF-16 request file name. `GetBytes` writes the level followed by UTF-16 path bytes.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs -->
