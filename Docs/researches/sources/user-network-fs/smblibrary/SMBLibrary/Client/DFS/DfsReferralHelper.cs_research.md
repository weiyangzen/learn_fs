<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs

## Purpose
`DfsReferralHelper` sends DFS referral requests through an `ISMBFileStore`.

## Important APIs and Types
`DfsReferralFileId` is the SMB2 sentinel file ID with both halves set to all ones. `MaxOutputBufferSize` is 8192. `GetDfsReferral()` builds a `RequestGetDfsReferral`, calls `DeviceIOControl()` with `FSCTL_DFS_GET_REFERRALS`, and parses `ResponseGetDfsReferral`.

## Control Flow
The helper sets referral level 4, serializes the requested DFS path, submits the IOCTL, and only constructs a response object when status is success and output bytes are non-null.

## State, Dependencies, and Integration
The helper is stateless. It bridges client file-store abstractions to DFS protocol structures and SMB2 IOCTL constants, but can be called through SMB1/SMB2 file stores if they implement `DeviceIOControl`.

## Risks and Test Signals
For SMB1, file handles are normally ushort FIDs, while this helper uses an SMB2 `FileID` sentinel; compatibility depends on the store implementation. Tests should cover successful referral parsing, non-success status passthrough, null output, buffer-size limits, and SMB1 versus SMB2 store behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs -->
