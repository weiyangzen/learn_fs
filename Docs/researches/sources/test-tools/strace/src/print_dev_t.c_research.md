<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_dev_t.c -->
# sources/test-tools/strace/src/print_dev_t.c

Purpose: prints encoded device numbers in raw, abbreviated, or verbose `makedev` form.

Important APIs/types/functions: `print_dev_t`, `major`, `minor`, and xlat verbosity helpers.

Control flow: prints raw hex unless abbrev-only mode, returns early in raw mode, otherwise prints or comments `makedev(major, minor)` according to xlat verbosity.

State and persistence behavior: no state.

Dependencies and integration points: used by stat/statfs/VFS/socket diag decoders; depends on `<sys/sysmacros.h>` and print-field helpers.

Risks: major/minor extraction follows libc macros and must match Linux device encoding expected by decoded structures.

Test signals: raw, abbrev, and verbose xlat modes with representative device numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_dev_t.c -->
