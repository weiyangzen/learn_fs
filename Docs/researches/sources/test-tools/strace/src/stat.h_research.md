# sources/test-tools/strace/src/stat.h

Purpose: internal normalized file-stat structure used by stat fetchers and printers.

Important APIs/types/functions: `struct strace_stat` fields for device, inode, rdev, size, blocks, blksize, mode, links, uid/gid, timestamps, nanoseconds, and `has_nsec`.

Control flow: header only; fetchers populate the normalized structure and printers consume it.

State and persistence behavior: none.

Dependencies and integration points: included by `stat.c`, `stat64.c`, stat fetch implementations, and common stat printing code.

Risks: normalized field widths must be wide enough for every supported kernel ABI. `has_nsec` controls timestamp precision and must be set correctly by fetchers.

Test signals: stat output with large inode/device/size values, nanosecond and non-nanosecond ABIs, uid/gid formatting, and device/rdev printing.
