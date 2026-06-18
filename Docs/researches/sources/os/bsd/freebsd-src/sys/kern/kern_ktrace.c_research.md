# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ktrace.c

## Purpose
Implements user-visible process tracing for `ktrace(2)` and `utrace(2)`, recording syscalls, returns, namei paths, genio data, signals, context switches, capability failures, faults, proc ctor/dtor events, structured records, sysctl names, arguments, environments, and extended errors.

## Key Interfaces
- Event emitters include `ktrsyscall()`, `ktrsysret()`, `ktrnamei()`, `ktrsysctl()`, `ktrgenio()`, `ktrpsig()`, `ktrcsw()`, `ktrstruct()`, `ktrstructarray()`, `ktrcapfail()`, `ktrfault()`, `ktrfaultend()`, and `ktrexterr()`.
- Process lifecycle hooks: `ktrprocexec()`, `ktrprocexit()`, `ktrprocctor()`, `ktrprocfork()`, and `ktruserret()`.
- Syscalls: `sys_ktrace()` and `sys_utrace()`.
- `ktr_get_tracevp()` exposes the trace vnode under process lock.

## State And Locking
`ktrace_mtx` protects the request free list, `p_traceflag`, `p_ktrioparms`, queued requests, and IO parameter refcounts. `ktrace_sx` serializes draining/writing. `TDP_INKTRACE` suppresses recursive tracing. Each traced process references `struct ktr_io_params`, containing vnode, credential, file-size limit, and refcount.

## Control Flow
Trace event generation allocates a `ktr_request` from a bounded pool, fills a versioned header, attaches fixed data and optional payload, then either writes immediately through VFS or queues to the process pending list for AST/user-return draining. `sys_ktrace()` opens and validates the trace file, then applies set/clear/clearfile operations to a pid, process group, or descendants. Writes append header, fixed type data, and dynamic payload with `VOP_WRITE`; on write failure tracing is disabled for that process.

## Integration Notes
Uses VFS, MAC checks, Capsicum capability failure reporting, process/proctree locks, AST callbacks, resource limits, credentials, and extended error conversion.

## Risks
Request pool exhaustion marks dropped records and emits only one warning until resized. Ordering across processes/threads writing the same vnode is explicitly weak. Permission and credential behavior is subtle: setuid exec disables tracing unless trace credentials have `PRIV_DEBUG_DIFFCRED`, and root-set traces carry `KTRFAC_ROOT`.
