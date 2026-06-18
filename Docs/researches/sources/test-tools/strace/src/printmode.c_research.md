# sources/test-tools/strace/src/printmode.c

Purpose: Prints file mode bitmasks in symbolic and numeric form.

Important APIs/types/functions: provides mode formatting helpers used by file-related syscall decoders. It maps file type and permission bits through xlat tables and preserves raw numeric output according to verbosity.

Control flow: accepts a mode value, emits file type bits, permissions, and special bits in the style selected by xlat verbosity. Unknown bits are preserved numerically.

State and persistence: stateless; depends only on current output verbosity.

Dependencies/integration: depends on `defs.h`, print flags helpers, and mode xlat tables. Integrated by `open`, `chmod`, `mkdir`, `mknod`, `stat`-style decoders, and anywhere `mode_t` is displayed.

Risks: file type bits overlap with permissions, so order and masks must be correct. Golden tests are sensitive to raw/abbrev/verbose formatting.

Test signals: chmod/open/mkdir tests with normal, special, file-type, unknown, raw, and verbose mode outputs.
