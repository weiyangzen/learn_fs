# sources/test-tools/liburing/test/nolibc.c

Purpose: validates liburing's nolibc helper `get_page_size()` against libc `sysconf(_SC_PAGESIZE)` on supported architectures.

Important APIs/types/functions: architecture preprocessor guards, `CONFIG_NOLIBC`, `../src/lib.h`, `get_page_size`, `sysconf`, and `T_EXIT_SKIP`.

Control flow: unsupported architectures compile a main that skips. Supported architectures define `CONFIG_NOLIBC`, include liburing internals, compare page-size values, and pass or fail.

State and persistence behavior: no mutable external state or persistence.

Dependencies and integration points: coupled to liburing internal `src/lib.h` and architecture support for nolibc implementations on x86, x86-64, aarch64, and riscv64.

Risks and test signals: failure means nolibc page-size detection differs from libc, which can break mmap/ring sizing paths in nolibc builds.
