# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.h

## Purpose

`xfs_trans_resv.h` defines transaction reservation structures, standard log count constants, directory reservation macros, and exported reservation calculation APIs.

## Main Content

- Defines `struct xfs_trans_res` with log reservation bytes, log operation count, and log flags.
- Defines `struct xfs_trans_resv` containing reservation entries for:
  - Writes and truncates.
  - Namespace operations.
  - Inode free/change.
  - Growfs.
  - Attribute operations.
  - Quotas.
  - Superblock.
  - Fsync timestamp/writeid.
  - Atomic ioend.
- Defines `M_RES(mp)` mount shorthand.
- Defines directory operation log reservation/count macros.
- Defines default and operation-specific log count constants.
- Retains older reflink log count constants for minimum log size calculations only.
- Declares full reservation calculation and individual deferred completion reservation helpers.
- Declares minimum-log-size reservation helpers.
- Declares atomic write reservation geometry helpers.

## Key Interfaces and Invariants

- Permanent reservations are indicated via `tr_logflags`, not by a separate type.
- Old reflink log count constants must not be used for runtime reservations.
- Directory operation macros depend on mount directory geometry and bmap reservation macros.

## Dependencies

Depends on XFS mount state and transaction space macros/types provided by surrounding libxfs headers.
