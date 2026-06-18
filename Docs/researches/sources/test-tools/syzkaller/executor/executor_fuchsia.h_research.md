# sources/test-tools/syzkaller/executor/executor_fuchsia.h

Purpose: Fuchsia executor adapter for Zircon/libc syscall execution without coverage support.

Important APIs and control flow: `os_init` maps the executor data segment through `syz_mmap`. `execute_syscall` invokes the generated call wrapper and converts Zircon status conventions for `zx_` calls into libc-style executor results: success returns 0, errors set `errno` to `(-res) & 0x7f` and return `-1`, while selected time/debug calls are treated as arbitrary-return helpers. Non-Zircon libc functions normalize 32-bit `-1` to pointer-width `-1`.

State and dependencies: includes `nocover.h`, so all coverage functions are no-ops. Depends on Zircon status/syscall headers, `strncmp`, and generated syscall wrappers.

Integration points: included by `executor.cc` for `GOOS_fuchsia`; shares common program decoding and output code.

Risks and tests: the errno mapping intentionally truncates Zircon statuses into a small range, which is enough for executor semantics but not a faithful status report. Because coverage is disabled, signal/coverage collection paths are unavailable on this target. Test signals are mainly target builds and executor machine checks.
