# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.h

## Purpose
Declares attr repair helper entry points used by other scrub repair code.

## API
- `xrep_xattr_swap`: exchange rebuilt tempfile attr fork with target attr fork.
- `xrep_xattr_reset_fork`: clear the target inode attr fork.
- `xrep_xattr_reset_tempfile_fork`: clear the tempfile attr fork after repair or cleanup.

## Notes
Forward-declares `struct xrep_tempexch` to avoid exposing tempfile exchange internals.
