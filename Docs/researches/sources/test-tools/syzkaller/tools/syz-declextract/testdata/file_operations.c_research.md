# sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c

Purpose: this fixture models Linux `struct file_operations` discovery, ioctl command extraction, nested helper ioctl dispatch, array initializers, ternary function initializers, and unused ioctl filtering.

Important APIs and flow: it includes UAPI ioctl constants and local headers, defines `FOO_IOCTL12`, simple operation callbacks, `foo_ioctl2` handling `FOO_IOCTL6`/`7`, and `foo_ioctl` handling `FOO_IOCTL1` through `5` and `10` through `12` before delegating to `foo_ioctl2`. It declares `const struct file_operations foo` with open/read/write/unlocked_ioctl/mmap callbacks; `mmap` uses a ternary expression to force extraction of the first function. It also declares an array `proc_ops[]` with two operation entries and an `unused` operations table whose ioctl constants should not surface as reachable interface descriptions.

State and persistence: no runtime state; all behavior is encoded in static const tables and switch statements.

Dependencies and integration: uses fixture `fs.h`, `file_operations.h`, and `unused_ioctl.h`. It is consumed by declextract golden tests to produce `file_ops`, `ioctls`, constants, and struct layout output.

Risks: initializer syntax and macro expansion are intentionally kernel-like. Changes to operation field names, ternary handling, or unused-interface pruning can change generated descriptions.

Test signals: paired JSON includes file operation entries, ioctl command metadata, `foo_ioctl_arg` struct layout, call facts from `foo_ioctl` to `foo_ioctl2`, and constants extracted from both macros and enums.
