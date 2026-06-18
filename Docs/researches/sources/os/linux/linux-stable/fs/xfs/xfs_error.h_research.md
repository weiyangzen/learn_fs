# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_error.h

## Purpose
Declares XFS error/corruption reporting helpers, debug errortag hooks, error levels, dump sizing, and panic tag constants.

## Main APIs
Provides prototypes for internal error, corruption, buffer corruption, buffer verifier, generic verifier, and inode verifier reporting. Macros `XFS_ERROR_REPORT` and `XFS_CORRUPTION_ERROR` capture file, line, and return address.

## Debug Configuration
Under `DEBUG`, declares errortag init/delete/test/delay/add/add-by-name/copy/clear helpers and macros that inject file/line context. Without `DEBUG`, errortag operations compile to disabled or `-ENOSYS` behavior.

## Panic Tags
Defines panic tag bits used by XFS alert paths and `XFS_PTAG_MASK`, with string mappings for sysctl-facing configuration.
