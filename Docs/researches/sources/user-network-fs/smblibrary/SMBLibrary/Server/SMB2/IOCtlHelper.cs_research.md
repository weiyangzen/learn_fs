<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs

## Purpose
SMB2 IOCTL/FSCTL handling. It validates FSCTL-only support, handles special control-code preconditions, resolves file handles when needed, delegates to `IFileStore.DeviceIOControl()`, and returns output buffers.

## APIs, Types, and Functions
`IOCtlHelper.GetIOCtlResponse()` is the only entry point. It recognizes DFS referral requests, `FSCTL_PIPE_WAIT`, `FSCTL_VALIDATE_NEGOTIATE_INFO`, and `FSCTL_QUERY_NETWORK_INTERFACE_INFO`, and returns `IOCtlResponse` or `ErrorResponse`.

## Control Flow, State, and Persistence
Non-FSCTL requests fail with `STATUS_NOT_SUPPORTED`. DFS referral controls fail with `STATUS_FS_DRIVER_REQUIRED`. Certain global FSCTLs must use all-ones `FileId`; other controls require a valid session open-file object. Successful or buffer-overflow store results become `IOCtlResponse` with the same control code and output. No durable state is modified.

## Dependencies and Integration
Called by SMB2 dispatch. It relies on `SMB2Session` open-file tables and backing stores implementing `DeviceIOControl()`.

## Risks and Test Signals
Risks include limited built-in FSCTL semantics, possible mismatch around global FSCTLs and share selection, returning buffer overflow as a normal response, and no validation of input shape per control code. Test global FSCTL file IDs, invalid file IDs, DFS referral failure, store success/error/buffer-overflow, and named-pipe controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs -->
