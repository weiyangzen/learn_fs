# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_fs.c

Read completely. This file dispatches SMB2 IOCTL FSCTL subcodes for `FILE_DEVICE_FILE_SYSTEM` and `FILE_DEVICE_NETWORK_FILE_SYSTEM`.

For filesystem-device FSCTLs, `smb2_fsctl_fs()` maps compression, sparse, zero-data, allocated-ranges, ODX read/write, file-region query, and selected unsupported/invalid control codes. It requires the current FID to be a disk file before dispatching. Sparse and ODX work is delegated to sibling files.

For network-filesystem-device FSCTLs, `smb2_fsctl_netfs()` maps snapshot enumeration, resume-key creation, copychunk, resiliency, network-interface info, validate-negotiate, and unknown codes. Most require a disk file; `FSCTL_VALIDATE_NEGOTIATE_INFO` and network-interface info do not.

`smb2_fsctl_get_resume_key()` returns the server’s opaque copychunk resume key as persistent ID, temporal FID, and padding. This key is later consumed by `smb2_fsctl_copychunk()`.

Compression support is minimal: get returns compression state zero and set accepts only zero, returning `NT_STATUS_COMPRESSION_DISABLED` for nonzero compression state. Notable implementation detail: `smb2_fsctl_get_compression()` encodes to `fsctl->in_mbc`; because this is a getter, this is worth checking against expected output-buffer usage.
