# sources/test-tools/syzkaller/executor/executor_test.h

Purpose: Test-OS executor adapter used by syzkaller unit/integration tests to simulate coverage and syscall execution in userspace.

Important APIs and control flow: `os_init` sets parent-death signal on Linux, maps the data region, and derives kernel bitness from host word size. `__sanitizer_cov_trace_pc` records instrumented PCs into the current thread coverage buffer after converting return addresses into synthetic kernel-text PCs. `execute_syscall` injects a coverage PC and invokes the generated call wrapper. Coverage APIs allocate anonymous buffers, reset counts, collect sizes, and support comparison-mode bookkeeping without real KCOV. `inject_cover`, `syz_inject_cover`, and `syz_inject_remote_cover` copy caller-provided coverage data into local or extra coverage buffers. Feature setup reports fault support and leak unsupported.

State and dependencies: synthetic `kernel_text_start` and `kernel_text_mask` must align with `sys/targets` expectations. Coverage buffers live in executor memory rather than kernel mappings.

Integration points: included for `GOOS_test`; used by `test.h` and fuzzer tests to exercise executor result paths deterministically.

Risks and tests: the sanitizer hook must remain uninstru­mented to avoid recursion. Synthetic PC values do not represent real kernel layout. This file is itself part of the test target; test signals include coverage injection, cover-filter tests, and executor package tests.
