# sources/test-tools/liburing/src/arch/aarch64/lib.h

## sources/test-tools/liburing/src/arch/aarch64/lib.h

Purpose: AArch64 page-size helper for liburing, including nolibc support.

Important APIs/functions: `__get_page_size` and cached `get_page_size`.

Control flow: with libc, call `sysconf(_SC_PAGESIZE)` and fallback to 4096. With nolibc, open `/proc/self/auxv`, read pairs of `Elf64_Off`, look for `AT_PAGESZ`, close fd, fallback to 4096. `get_page_size` caches first result in a static variable.

State and persistence: process-local static cache; reads procfs in nolibc mode.

Dependencies/integration: included by architecture-specific liburing internals; nolibc path depends on `__sys_open`, `__sys_read`, and `__sys_close`.

Risks: cache is unsynchronized but benign. Nolibc auxv parser assumes pair size and readable procfs. Fallback 4096 may be wrong on unusual systems if auxv/procfs unavailable.

Test signals: architecture CI build and runtime mapping behavior using page size.
