# File Research: sources/virtualization/libguestfs/lib/umask.c

Thread-safe current umask retrieval.

Important behavior:
- `guestfs_int_getumask` first tries `/proc/self/status` and falls back to a fork-based method.
- `/proc` parser looks for `Umask: %o`; missing `/proc` or missing field triggers fallback, while other open errors are fatal.
- Fallback creates a CLOEXEC pipe, forks, and has the child call `umask(0)` and write the previous mask back.
- Child uses only async-safe operations after fork.
- Parent reads the mask and waits using libguestfs wait helpers.
- Command-style errors are reported if the child exits unsuccessfully.

Filesystem relevance:
- Used during launch diagnostics and helps preserve/understand host file creation permissions for temporary files and overlays.
