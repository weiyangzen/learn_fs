# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/fs.h

Purpose: this fixture header provides a minimal Linux-like `struct file_operations` and helper functions used by declextract C fixtures.

Important APIs and flow: `struct file_operations` contains callback fields for `open`, `read`, `write`, `read_iter`, `write_iter`, `unlocked_ioctl`, and `mmap`. Static helpers `alloc_fd`, `__fget_light`, and `from_kuid` model fd allocation, fd consumption, and uid conversion return facts.

State and persistence: no persistent state; functions return constants or no-op.

Dependencies and integration: included by `file_operations.c`, `functions.c`, and `scopes.c`. Its function definitions appear in golden JSON outputs when reachable or visible.

Risks: the header is intentionally incomplete; it only contains fields needed by fixtures and may not reflect full kernel API evolution.

Test signals: validates recognition of file operation callback fields and helper functions in the generated JSON call/fact graph.
