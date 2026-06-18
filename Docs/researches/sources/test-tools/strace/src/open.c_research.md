<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/open.c -->
# sources/test-tools/strace/src/open.c

Purpose: decodes `open`, `openat`, `openat2`, `creat`, and shared directory-fd/open-flag formatting.

Important APIs/types/functions: `print_dirfd`, `sprint_open_modes`, `tprint_open_modes`, `decode_open`, `print_open_how`, `SYS_FUNC(open)`, `openat`, `openat2`, and `creat`.

Control flow: open-like syscalls print path, flags, optional mode for `O_CREAT`/`__O_TMPFILE`, and return fd semantics. `openat` prints `dirfd` first. `openat2` fetches `struct open_how`, prints flags/mode/resolve flags, and emits nonzero trailing bytes for larger user-provided sizes.

State and persistence behavior: no durable state, except `print_dirfd` updates `tcp->last_dirfd` when SELinux context support is enabled and may read `/proc/<pid>/cwd` for associated info.

Dependencies and integration points: depends on `kernel_fcntl.h`, `<linux/openat2.h>`, open flag xlats, path/fd printers, number-set decode-fd options, and proc pid helpers.

Risks: open flag formatting must split access mode from other flags correctly. `openat2` structure size is user-provided and must avoid over-reading.

Test signals: all open variants, `AT_FDCWD` with cwd decoding, `O_CREAT`, `O_TMPFILE`, unknown flags, `open_how` short/extended sizes, resolve flags, and fd return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/open.c -->
