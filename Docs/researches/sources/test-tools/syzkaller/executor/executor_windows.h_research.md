# sources/test-tools/syzkaller/executor/executor_windows.h

Purpose: Windows executor adapter for data allocation, syscall wrapper invocation, and pipe I/O shims.

Important APIs and control flow: `os_init` reserves and commits the executor data region at the requested address with `PAGE_EXECUTE_READWRITE`. `execute_syscall` calls the generated wrapper under structured exception handling and returns `-1` on exception. The header includes `nocover.h`, so all coverage functions are stubs. It remaps `read` and `write` macros to `read_win` and `write_win`, which call `ReadFile`/`WriteFile` on `_get_osfhandle(pipe_id)` and return byte counts.

State and dependencies: depends on Windows handles and C runtime fd-to-handle conversion. No persistent coverage state is maintained.

Integration points: selected by `executor.cc` for `GOOS_windows`; complements `common_windows.h` threading/events/temp-dir support.

Risks and tests: `read_win`/`write_win` ignore API failure details and return zero bytes on failure, so protocol failures surface as short reads/writes in common executor code. Coverage and comparisons are unavailable. Test signals are target builds and Windows executor runtime checks.
