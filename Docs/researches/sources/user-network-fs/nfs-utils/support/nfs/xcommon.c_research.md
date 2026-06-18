# sources/user-network-fs/nfs-utils/support/nfs/xcommon.c

Purpose: shared allocation, string, path, and error helpers imported from mount/util-linux ancestry.

Important APIs and globals: `at_die` optional callback, `xstrndup()`, `xstrconcat2()`, `xstrconcat3()`, `xstrconcat4()`, `nfs_error()`, `canonicalize()`, `die()`, `xmalloc()`, `xrealloc()`, `xfree()`, and `xstrdup()`.

Control flow: allocation wrappers call `die(EX_SYSERR, ...)` on failure except zero-size `xmalloc()` returns NULL. Concatenation helpers treat NULL inputs as empty strings, and the 3/4-argument variants free their first argument when it was non-NULL. `canonicalize()` preserves special pseudo-filesystem names and otherwise returns `realpath()` output or a copy of the original path.

State and persistence: `at_die` is a process-global hook invoked before fatal exit. No durable state.

Dependencies and integration: used by mount/NFS parsing utilities for fail-fast allocation. Depends on NLS `_()` and `xcommon.h`.

Risks: fatal allocation behavior is unsuitable in library paths that should report `ENOMEM`. `xstrconcat3/4()` freeing the first argument is nonobvious and dangerous with string literals or shared ownership. `canonicalize()` returns unresolved paths unchanged, which callers must not confuse with verified canonical paths.

Test signals: allocation failure hooks, NULL string arguments, first-argument ownership in concat helpers, pseudo-filesystem canonicalize exceptions, realpath success/failure, and fatal exit behavior.
