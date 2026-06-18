# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.h

Declares shared fsck utility functions and status flags.

Exports:
- Error and warning reporting helpers.
- Raw/block device name conversion.
- Root/device setup and hot-root detection.
- Checked allocation wrappers.
- `checkfstab`, the preen/fstab scheduling entry point.

Defines dispatcher flags:
- `CHECK_PREEN`
- `CHECK_VERBOSE`
- `CHECK_DEBUG`

This header is included by the generic fsck front-end and by filesystem-specific checkers for consistent diagnostics, device handling, and fstab orchestration.
