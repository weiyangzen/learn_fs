## sources/user-network-fs/nfs-utils/utils/statd/misc.c

Purpose: Small allocation helpers for statd.

Important APIs/types/functions: `xmalloc` and `xstrdup` wrap allocation and log fatal errors with `xlog_err` on failure.

Control flow: `xmalloc(0)` returns NULL; otherwise allocation failure terminates via logging behavior. `xstrdup` similarly assumes non-NULL input.

State and persistence: No state.

Dependencies and integration: Used by notification-list and simulator code for fail-fast allocation semantics.

Risks and test signals: Callers do not consistently handle NULL because these helpers are intended to abort on memory exhaustion. Unit tests can cover zero-size allocation and successful duplication; fault injection should confirm expected fatal logging path.
