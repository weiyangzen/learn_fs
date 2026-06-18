# sources/test-tools/fio/oslib/libmtd_xalloc.h

Purpose: allocation wrappers imported with MTD utility code.

Important APIs/functions: static inline `xmalloc()`, `xcalloc()`, `xzalloc()`, `xrealloc()`, `xstrdup()`, and `_GNU_SOURCE`-guarded `xasprintf()`. Functions abort through `sys_errmsg_die()` on nonzero-size allocation failure.

Control flow and state: no persistent state; wrappers delegate to libc allocation routines and centralize failure handling.

Dependencies and integration: assumes `sys_errmsg_die()` is available from `libmtd_common.h`, so this header is normally included after common helpers.

Risks: allocation failure exits the process rather than returning an error, which may be unexpected inside fio. Functions are marked unused to silence warnings in translation units that include but do not use them.

Test signals: compile with and without `_GNU_SOURCE`; fault-injection allocation tests would need to accept process exit semantics.
