# File Research: sources/os/linux/linux/fs/exec.c

## Purpose
Implements Linux process image replacement for `execve`, `execveat`, and kernel-driven `kernel_execve`. It owns binary-format dispatch, argument/environment staging, credential preparation and commitment, address-space replacement, thread-group collapse, close-on-exec handling, and exec-related sysctl wiring.

## Main Interfaces
- Exported helpers: `__register_binfmt`, `unregister_binfmt`, `open_exec`, `copy_string_kernel`, `setup_arg_pages`, `begin_new_exec`, `would_dump`, `setup_new_exec`, `finalize_exec`, `remove_arg_zero`, `set_binfmt`.
- Syscalls: `execve`, `execveat`, plus compat variants under `CONFIG_COMPAT`.
- Sysctl: `/proc/sys/fs/suid_dumpable` when `CONFIG_SYSCTL`.

## Key Data Flow
`do_execveat_common()` opens the target with execute intent, creates `linux_binprm`, counts and copies argv/envp backward onto the nascent stack, enforces stack/argument limits, and calls `bprm_execve()`. `bprm_execve()` prepares credentials, checks unsafe exec states, invokes LSM hooks, and runs `exec_binprm()`. `exec_binprm()` repeatedly calls binary format loaders through `search_binary_handler()` to support interpreter chains.

The point of no return is `begin_new_exec()`: credentials are finalized from the actual executable, other threads are killed via `de_thread()`, files and signal handlers are unshared/reset, the new `mm_struct` replaces the old one, dumpability and `comm` are updated, credentials are committed, and optional execfd handoff is installed. `setup_new_exec()` later drops exec locks and releases the old mm.

## Dependencies
Tightly coupled to VFS path/open code, LSM hooks, binfmt modules, mm/VMA setup, signal/thread-group internals, credentials/user namespaces, audit, ptrace, proc connector, perf, rseq, io_uring, coredump policy, and architecture-specific stack/start-thread behavior.

## Notable Invariants And Risks
- After `bprm->point_of_no_return`, failures must kill the task rather than return to old userspace.
- `cred_guard_mutex` and `exec_update_lock` ordering is central to ptrace, credentials, and mm replacement safety.
- argv/envp accounting temporarily charges pages to the old mm for OOM behavior.
- setuid/setgid handling is guarded by mount flags, `no_new_privs`, idmapped mounts, namespace mappings, and LSM hooks.
- Binary-handler recursion is bounded to prevent interpreter loops.
