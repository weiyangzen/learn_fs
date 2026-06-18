# sources/test-tools/strace/tests/xutimes.c

Purpose: `xutimes.c` is a strace decoder test template for `utimes`-family syscalls, parameterized by `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, and `TEST_STRUCT`. It drives the raw syscall with crafted pathname and timeval pointers, then prints the exact expected strace rendering.

Important APIs and control flow: `print_tv` formats `TEST_STRUCT` timestamp pairs with `zero_extend_signed_to_ull` and `print_time_t_usec`; `k_utimes` calls `syscall(TEST_SYSCALL_NR, pathname, times)` and stores `sprintrc(rc)` in file-static `errstr`; `main` allocates tail-guarded path and timeval storage, tests NULL, empty, valid, unterminated, inaccessible, invalid high-bit, out-of-range, invalid-usec, and valid timeval cases, then prints the synthetic trace lines.

State and persistence: state is only process-local test memory plus file-static `errstr`; no durable state is written. The test intentionally mutates the filename terminator and timeval contents between syscall attempts.

Dependencies and integration: depends on the strace test harness for `tail_memdup`, `TAIL_ALLOC_OBJECT_CONST_ARR`, `kernel_ulong_t`, `sprintrc`, `F8ILL_KULONG_SUPPORTED`, and time formatting helpers. It is compiled multiple ways by defining the syscall and struct macros.

Risks and test signals: correctness depends on exact kernel errno behavior, pointer fault layout, ABI-width extension, and timeval signedness. Strong signals are matching expected output for bad pointers, invalid microseconds, and printed decoded timestamps across native and compat ABIs.
