<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uid.c -->
# sources/test-tools/strace/src/uid.c

Purpose: strace syscall decoder implementation for `getuid`, `setfsuid`, `setuid`, `getresuid`, `setreuid`, `setresuid`, `chown`, `fchown`...; it prints syscall arguments/results using strace formatting helpers.

Important APIs/types/functions:
- SYS_FUNC handlers: `getuid`, `setfsuid`, `setuid`, `getresuid`, `setreuid`, `setresuid`, `chown`, `fchown`, `setgroups`, `getgroups`
- Helper functions include `get_print_uid`, `printuid`, `print_gid`, `print_groups`
- Direct includes: `"defs.h"`
- Local/exported macros: `SIZEIFY`, `SIZEIFY_`, `SIZEIFY__`, `printuid`, `sys_chown`, `sys_fchown`, `sys_getgroups`, `sys_getresuid`, `sys_getuid`, `sys_setfsuid`, `sys_setgroups`, `sys_setresuid`...

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uid.c -->
