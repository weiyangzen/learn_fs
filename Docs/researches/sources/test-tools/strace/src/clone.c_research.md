<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/clone.c -->
## sources/test-tools/strace/src/clone.c

Purpose: Decodes process/thread creation and namespace-affecting syscalls: `clone`, `clone3`, `setns`, `unshare`, and `fork`.

Important APIs and types: Argument-position macros per architecture, `namespace_auxstr_init`, `read_namespace_id`, `get_namespace_auxstr`, `print_tls_arg`, `SYS_FUNC(clone)`, `SYS_FUNC(clone3)`, `SYS_FUNC(setns)`, `SYS_FUNC(unshare)`, and `SYS_FUNC(fork)`.

Control flow: `clone` prints stack/flags/signal on entry and defers pointer-output arguments until exit when flags require parent tid, pidfd, tls, child tid, or namespace aux strings. `clone3` fetches `struct clone_args`, prints fields conditionally by flags and provided size, prints tail bytes for oversized structs, and revisits output fields on successful exit. `setns` and `unshare` optionally defer completion so namespace IDs can be printed after success. `fork` returns decoded with TGID return formatting.

State and persistence: Static `show_namespace` is enabled by `namespace_auxstr_init`. Namespace aux strings use static buffers and `/proc/<pid>/ns/*` readlink calls. `clone3` has no tcb private allocation but re-fetches the tracee struct on exit.

Dependencies and integration: Depends on `scno.h`, `<linux/sched.h>`, `xstring.h`, `unistd.h`, clone/setns/unshare xlat tables, pid translation, fd printing, user-desc printing, and auxstr return handling.

Risks: Architecture-specific argument order is fragile. Namespace aux strings depend on `/proc`, pid namespace translation, and syscall success. `clone3` size-gating must handle old and future struct layouts without over-reading.

Test signals: Tests should cover architecture personalities, `clone2` stack size, CSIGNAL-only flags, pidfd and parent/child tid outputs, tls printing, `clone3` short/oversized structs, set_tid arrays, cgroup fd, namespace aux output, and failed syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/clone.c -->
