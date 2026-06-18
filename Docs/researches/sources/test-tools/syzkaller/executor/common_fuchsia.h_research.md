# sources/test-tools/syzkaller/executor/common_fuchsia.h

Purpose: This shared syzkaller header supplies Fuchsia-specific executor/csource primitives: exception-based non-failing memory access, simple event synchronization, Zircon handle pseudo-syscalls, VMAR mapping, future-time generation, and no-sandbox entry.

Important APIs and types: Crash recovery uses thread-local `skip_segv`, `segv_env`, `segv_handler`, `update_exception_thread_regs`, `ex_handler`, `install_segv_handler`, and `NONFAILING`. Threading uses a spin-based `event_t` with `event_init`, `event_reset`, `event_set`, `event_wait`, `event_isset`, and `event_timedwait`. Pseudo-syscalls include `syz_mmap`, `syz_process_self`, `syz_thread_self`, `syz_vmar_root_self`, `syz_job_default`, and `syz_future_time`. Sandbox integration exposes `do_sandbox_none`, and `CAST` works around incompatible function-pointer calls in generated C.

Control flow and state: Fuchsia faults are handled by a process exception channel. The handler thread waits for exceptions, reads exception info, rewrites the faulting thread’s instruction pointer to `segv_handler`, marks the exception handled, and lets `NONFAILING` longjmp or exit depending on `skip_segv`. `syz_mmap` creates a VMO, maps it at a requested root-VMAR-relative address with overwrite/read/write flags, closes the VMO, and returns the Zircon status.

Dependencies and integration points: It depends on Zircon syscalls, fdio, pthreads, and common executor functions (`debug`, `failmsg`, `doexit`, `current_time_ms`, `loop`). `common.h` includes it for `GOOS_fuchsia`.

Risks and test signals: Risks include exception-channel lifetime, rewriting registers for unsupported architectures, spin-wait CPU cost, VMAR address calculation, and handle values being returned as integer pseudo-syscall results. Tests should cover amd64/arm64 exception recovery, `NONFAILING` success/failure, `syz_mmap` fixed-address mapping, event timeouts, and handle pseudo-syscall validity.
