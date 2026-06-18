# File Research: sources/local-fs/xfsprogs/libxfs/xfs_symlink_remote.c

This file implements remote symlink block accounting, symlink block header creation and verification, inline-to-remote conversion, shortform verification, remote symlink reading, writing, and truncation.

`xfs_symlink_blocks` calculates the number of filesystem blocks needed for a path, accounting for a CRC symlink header in each contiguous block. `xfs_symlink_hdr_set` initializes the v5 remote symlink header when CRCs are enabled: magic, offset, bytes, meta uuid, owner inode, block address, and buffer ops. Non-CRC filesystems have no remote symlink header. `xfs_symlink_hdr_ok` checks per-block offset, byte count, and owner against expected values after the buffer verifier has checked structural fields.

`xfs_symlink_verify` is the structural verifier for CRC-enabled remote symlink buffers. It checks magic, metadata uuid, buffer disk address, offset+bytes below max symlink length, nonzero owner, and log sequence validity. Read verification checks checksum first; write verification checks structure, stamps the log item LSN if available, and updates the checksum. `xfs_symlink_buf_ops` exports these routines.

`xfs_symlink_local_to_remote` converts an inode-local symlink fork to a remote buffer. Non-CRC filesystems copy raw fork data into the buffer. CRC filesystems write a header then copy the target data after the header and log the initialized range.

`xfs_symlink_shortform_verify` validates in-memory inline symlink contents: nonzero size, nonnegative and below `XFS_SYMLINK_MAXLEN`, no embedded NUL before the terminator, and a terminating NUL byte.

`xfs_symlink_remote_read` requires the inode lock, reads the file block mapping for the remote target, reads each mapped buffer with symlink verifier ops, validates header owner/offset/length on CRC filesystems, copies chunks into the caller buffer, marks inode symlink sickness on metadata corruption, and NUL terminates the result.

`xfs_symlink_write_target` writes a symlink either inline or into remote blocks. Inline symlinks use `xfs_init_local_fork` and log inode data/core. Remote symlinks allocate mappings with `xfs_bmapi_write`, update inode size, fill each mapped buffer with optional CRC header plus target chunk, mark buffer type as symlink, and log written ranges.

`xfs_symlink_remote_truncate` invalidates all remote symlink buffers and unmaps the extents with `xfs_bunmapi`; if unmapping reports no progress it marks the inode symlink metadata sick and returns corruption.
