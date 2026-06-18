# sources/test-tools/syzkaller/executor/executor_darwin.h

Purpose: Darwin/XNU executor adapter with KSANCOV coverage support.

Important APIs and control flow: `os_init` maps the data segment and forces `is_kernel_64_bit = false` because KSANCOV returns 32-bit PCs plus an offset. `execute_syscall` invokes pseudo-syscalls or `__syscall`. `cover_open` opens KSANCOV, configures trace mode before mapping, and computes max entries from `kCoverSize`. `cover_mmap` maps the KSANCOV trace region and records data bounds. `cover_enable` attaches coverage to the current thread and rejects comparison or extra coverage. `cover_reset` restarts tracing, and `cover_collect` updates size, PC array offset, and kernel offset.

State and dependencies: depends on XNU `ksancov.h` APIs and assumes trace-PC mode only. `cover_t::pc_offset` reconstructs full PCs from truncated trace entries.

Integration points: included for `GOOS_darwin` by `executor.cc`; result serialization remains the common executor path.

Risks and tests: comments note required C++ fixes in upstream XNU headers. Unsupported TRACE_CMP and extra coverage fail hard. Coverage size assumptions are checked at mmap time. Test signals are target build/runtime coverage rather than local unit tests in this subset.
