<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_version.c -->
# sources/test-tools/strace/src/print_kernel_version.c

Purpose: prints packed Linux kernel version values.

Important APIs/types/functions: `print_kernel_version` and `KERNEL_VERSION`-style major/minor/patch extraction.

Control flow: prints raw hex unless abbrev-only mode; in non-raw modes also emits `KERNEL_VERSION(major, minor, patch)` as value or verbose comment.

State and persistence behavior: no state.

Dependencies and integration points: used by ioctl or syscall decoders that expose packed kernel version integers.

Risks: assumes the Linux `KERNEL_VERSION` packing layout `(major << 16) | (minor << 8) | patch`.

Test signals: raw/abbrev/verbose xlat modes and representative version values including high major/minor bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_version.c -->
