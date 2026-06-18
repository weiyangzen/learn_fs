# File Research: sources/os/linux/linux/fs/xfs/xfs_error.h

Declares XFS error/corruption reporting APIs, debug errortag APIs, and panic tag constants.

Key contents:
- Reporting functions for generic internal errors, corruption errors, buffer corruption, buffer verifier errors, generic verifier errors, and inode verifier errors.
- Macros `XFS_ERROR_REPORT` and `XFS_CORRUPTION_ERROR` capture file, line, and return address.
- Defines error levels and corruption dump length.
- Under DEBUG, declares errortag init/test/delay/add/copy/clear helpers; non-debug builds provide inert or `-ENOSYS` stubs.
- Defines panic tag bits and string mappings for sysctl-controlled panic behavior.

This header is included widely by XFS metadata verification and recovery code.
