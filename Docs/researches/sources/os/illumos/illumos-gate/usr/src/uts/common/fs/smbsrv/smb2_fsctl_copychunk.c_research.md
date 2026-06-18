# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_copychunk.c

Read completely. This file implements `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`, plus Apple server-side copy behavior.

`smb2_fsctl_copychunk()` validates the destination handle, access rights, output buffer size, resume key, source handle, source access, and chunk count. Resume keys are the opaque 24-byte blobs produced by `FSCTL_SRV_REQUEST_RESUME_KEY`, internally carrying SMB2 persistent and temporal file IDs. Limits are controlled by `smb2_copychunk_max_cnt`, `smb2_copychunk_max_seg`, and `smb2_copychunk_max_total`.

Chunk-array decoding is handled by `smb2_fsctl_copychunk_decode()`, which validates nonzero per-chunk lengths, maximum segment size, and total size. `smb2_fsctl_copychunk_array()` processes normal chunk lists and returns partial progress through `copychunk_resp`. `smb2_fsctl_copychunk_1()` checks source and destination byte-range locks, then delegates the copy to `smb2_sparse_copy()`.

Apple behavior is implemented in `smb2_fsctl_copychunk_aapl()`: when AAPL extensions are active, `chunk_cnt == 0` means copy the whole file. It loops until EOF, cancellation, timeout, or error, using a tunable timeout, and then calls `smb2_fsctl_copychunk_meta()` to copy attributes and DACL metadata. Metadata copying bypasses normal ofile WRITE_DAC checks but still relies on filesystem-level checks.

The IOCTL layer has special handling for this FSCTL because it may return an error status with a data payload containing server limits or partial-copy results.
