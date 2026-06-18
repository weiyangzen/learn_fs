# File Research: sources/virtualization/virtiofsd/src/seccomp.rs

## Purpose

This file builds and loads virtiofsd’s seccomp filter. It initializes a libseccomp context with a default action and explicitly allowlists syscalls needed by daemon startup, sandboxing, vhost-user transport, FUSE request handling, filesystem operations, threading, memory management, and optional remote logging.

## Main Types And Functions

- `Error`: failures for initializing seccomp, adding an allow rule, or loading the filter.
- `SeccompAction`: default action options: `Allow`, `Kill`, `Log`, `Trap`.
- `impl From<SeccompAction> for u32`: maps to libseccomp actions.
- `allow_syscall!`: helper macro converting a syscall constant to `i32`, adding an allow rule, and returning `AllowSeccompSyscall` on failure.
- `enable_seccomp(action, allow_remote_logging)`: constructs, populates, loads, and releases the seccomp context.

## Behavior

`enable_seccomp()` calls `seccomp_init(action.into())`, where `action` is the default action for non-allowlisted syscalls. It then invokes `allow_syscall!` for each permitted syscall. After all rules are added, it calls `seccomp_load(ctx)` and then `seccomp_release(ctx)`.

The allowlist is architecture-aware using `cfg` gates for syscalls that only exist or are only needed on selected targets, such as `epoll_create`, `epoll_wait`, `fstat`, `getdents`, `newfstatat`, `_llseek`, `open`, `renameat`, `sigreturn`, `time`, and `unlink`.

## Syscall Coverage

The allowlist covers:

- vhost-user socket and messaging: `accept4`, `recvmsg`, `sendmsg`, optional `sendto`.
- Event loops and notification: `epoll_*`, `eventfd2`, `futex`.
- Filesystem operations: `openat`, `openat2`, `open_by_handle_at`, `read`, `write`, `pread*`, `pwrite*`, `readv`, `writev`, `copy_file_range`, `fallocate`, `ftruncate`, `fsync`, `fdatasync`, `syncfs`, `getdents64`, xattrs, links, mkdir/mknod, rename, unlink, symlink, stat/statx/statfs, flock, lseek.
- Sandbox and privilege transitions: `capget`, `capset`, `setgroups`, `setresuid`, `setresgid`, `unshare`, `prctl`.
- Memory and process runtime: `brk`, `clone`, `clone3`, `mmap`, `mprotect`, `mremap`, `munmap`, `madvise`, `exit`, `exit_group`, signal syscalls, `getpid`, `gettid`, `getrandom`, scheduler calls.
- Compatibility/runtime support: `rseq` on GNU, `tkill` for older systems, `membarrier`, `umask`.

## Integration Points

This file must stay synchronized with syscall usage in:

- `read_dir.rs`: `getdents64`, `lseek`.
- `sandbox.rs`: `unshare`, `setresuid`, `setresgid`, `setgroups`, `prctl`, mount-related wrappers, process control.
- `server.rs`: file, xattr, directory, copy, sync, and read/write syscalls through filesystem backends.
- `vhost_user.rs`: epoll/eventfd/socket/vhost-user runtime.
- `util.rs`: `flock`, `pidfd_open`, `fork`, `poll`, `waitpid`, capability operations.

## Risks And Edge Cases

- New filesystem or sandbox functionality can fail under seccomp unless the syscall is added here.
- The default action can be `Kill`, `Trap`, or `Log`, so missing allowlist entries may become fatal depending on configuration.
- The allowlist is syscall-level only; it does not constrain syscall arguments.
- If `seccomp_rule_add` fails partway through, the context is not explicitly released before returning.
