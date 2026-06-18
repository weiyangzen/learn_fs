# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_ioctl.c

Purpose: handles PVFS ioctl requests with minimal supported behavior, mostly returning compatibility statuses.

Important APIs and functions: `pvfs_ioctl` dispatches by raw ioctl level. `pvfs_ioctl_old` returns a DOS server error for the old ioctl interface. `pvfs_ntioctl` validates an open file handle and supports `FSCTL_SET_SPARSE` as a successful no-op with an empty output blob.

Control flow: old SMB ioctl returns `ERRSRV/ERRerror`. NT ioctl resolves the file via `pvfs_find_fd`, rejects invalid handles, recognizes sparse-file marking, and otherwise returns `NT_STATUS_NOT_SUPPORTED`. SMB2 ioctl with or without a handle returns `NT_STATUS_INVALID_DEVICE_REQUEST` to satisfy compatibility tests.

State and persistence: no persistent state is changed. `FSCTL_SET_SPARSE` does not mark sparse state on disk.

Dependencies and integration points: called through the NTVFS POSIX backend ioctl callback and uses SMB constants plus PVFS file lookup.

Risks: sparse support is only nominal; callers expecting actual sparse allocation behavior will not get it. SMB2 returns a deliberately different status from NT ioctl unsupported cases. Test signals include invalid handle, successful `FSCTL_SET_SPARSE` empty blob, unsupported NT functions, old ioctl DOS status, SMB2 invalid-device status, and invalid level handling.
