# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_exec_fd.c

## Summary
Implements exec-time file descriptor tracing and standard-descriptor repair for privileged execs.

## Main Responsibilities
- Emits ktrace records for every open file descriptor during exec.
- Ensures descriptors 0, 1, and 2 are open by attaching `/dev/null` where needed.
- Logs a warning when setuid/setgid execution inherited closed standard descriptors.

## Important Behavior
`fd_ktrexecfd()` walks the current process descriptor table with atomic loads and records descriptor number plus file type.

`fd_checkstd()` allocates descriptors for closed stdin/stdout/stderr, opens `/dev/null` read-write, attaches vnode file operations, and asserts allocated descriptors are below 3. It logs parent uid/pid/command context for the unsafe invocation.

## Dependencies
Uses file descriptor tables, atomic descriptor table loads, `ktr_execfd()`, `fd_allocfile()`, `vn_open()`, vnode file operations, `/dev/null`, process locks, and kauth credentials.

## Risks
The repair path assumes `fd_allocfile()` returns the lowest available descriptor and asserts it is one of 0..2. Errors opening `/dev/null` abort the partially allocated file descriptor.
