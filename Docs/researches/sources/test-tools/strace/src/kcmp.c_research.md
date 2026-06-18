# sources/test-tools/strace/src/kcmp.c

Purpose: decodes `kcmp` process-resource comparison calls.

Important APIs/types/functions: `SYS_FUNC(kcmp)`, `PRINT_FIELD_PIDFD`, `printfd_pid_tracee_ns`, `printpid`, `struct kcmp_epoll_slot`, and `kcmp_types`.

Control flow: prints `pid1`, `pid2`, and comparison `type`. For `KCMP_FILE`, `idx1` and `idx2` are rendered as file descriptors in the respective process namespaces. For `KCMP_EPOLL_TFD`, `idx1` is a fd and `idx2` points to a `kcmp_epoll_slot` whose fds and offset are decoded. Other known resource types omit index printing; unknown types print raw hex indices.

State and persistence behavior: no persistent state. Only `KCMP_EPOLL_TFD` reads tracee memory.

Dependencies and integration points: depends on `<linux/kcmp.h>`, PID/fd namespace-aware printers, and generated `kcmp_types` xlat entries.

Risks: fd rendering must use the PID associated with each index; using the tracer namespace would be misleading. Unknown future `KCMP_*` types fall back to raw indices.

Test signals: cover known resource types, file comparison with two process namespaces, epoll slot decoding and inaccessible slot pointer, and unknown type fallback.
