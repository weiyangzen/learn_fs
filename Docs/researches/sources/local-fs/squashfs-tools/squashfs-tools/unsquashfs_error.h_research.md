# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_error.h

Small error-policy adapter for `unsquashfs`.

Defines:
- `INFO()` routed through `progressbar_info()` so informational output cooperates with the progress bar.
- `EXIT_UNSQUASH()` as unconditional fatal `BAD_ERROR()`.
- `EXIT_UNSQUASH_IGNORE()` as fatal unless `ignore_errors` is set, in which case it logs through `ERROR()`.
- `EXIT_UNSQUASH_STRICT()` as non-fatal logging unless `strict_errors` is set, in which case it aborts.

The macros centralize how CLI flags alter extraction error behavior without spreading policy checks throughout the code.
