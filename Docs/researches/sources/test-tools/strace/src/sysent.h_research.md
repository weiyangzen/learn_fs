# sources/test-tools/strace/src/sysent.h

Purpose: defines syscall table entry shape and syscall classification flags.

Important APIs/types/functions: `struct_sysent` fields `nargs`, `sys_flags`, `sen`, `sys_func`, and `sys_name`; flags such as `TRACE_FILE`, `TRACE_NETWORK`, `TRACE_PROCESS`, `SYSCALL_NEVER_FAILS`, `MEMORY_MAPPING_CHANGE`, `TRACE_SECCOMP_DEFAULT`, `COMPAT_SYSCALL_TYPES`, `TRACE_CREDS`, `TRACE_CLOCK`, and `COMM_CHANGE`.

Control flow: no executable control flow; generated syscall tables instantiate this structure and flags drive filtering and side effects in `syscall.c`.

State and persistence behavior: type/constant declarations only.

Dependencies and integration points: consumed by syscall tables, qualifiers, seccomp filtering, mmap cache invalidation, comm cache refresh, and return-error handling.

Risks: flag bit assignments are shared ABI inside strace; accidental overlap or wrong table flags cause filtering/side effects to misbehave.

Test signals: compile generated tables, verify `%file/%net/%clock` classes, mmap cache invalidation for mapping-changing syscalls, and no-error handling for never-failing syscalls.
