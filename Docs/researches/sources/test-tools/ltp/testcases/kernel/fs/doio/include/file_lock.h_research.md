# sources/test-tools/ltp/testcases/kernel/fs/doio/include/file_lock.h

Purpose: `file_lock.h` declares the doio suite's file-lock wrapper API and provides fallback lock flag definitions on platforms that do not expose BSD-style `LOCK_*` constants in the expected headers.

Important APIs and types: it exports `extern char Fl_syscall_str[128]`, `file_lock(int, int, char **)`, and `record_lock(int, int, int, int, char **)`. On Sun and HP-UX builds it defines `LOCK_NB`, `LOCK_UN`, `LOCK_EX`, and `LOCK_SH`.

Control flow: the header has no implementation. It is consumed by callers that request whole-file or byte-range advisory locks and receive `0`/`-1` style status plus optional error text.

State and persistence behavior: `Fl_syscall_str` is shared process-global diagnostic state from the implementation. Actual lock persistence is kernel state tied to process/file descriptor semantics.

Dependencies and integration points: `file_lock.c` implements the declarations, and `growfiles.c` uses `file_lock()` through its `lkfile()` helper. The API abstracts the suite away from direct `struct flock` construction for common lock cases.

Risks: fallback constants are only defined for selected platforms; other systems must already provide compatible `LOCK_*` values. `char **` error output has no const qualifier or ownership annotation. `Fl_syscall_str` is mutable global state and not thread-safe.

Test signals: compile-time coverage should verify constants resolve on target platforms. Runtime coverage should check exclusive, shared, unlock, nonblocking, range, and invalid flag paths through the implementation.
