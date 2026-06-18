# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.c

Purpose: Provides credential-aware wrapper functions around the LizardFS C API. Each wrapper creates a `liz_context_t` from Ganesha credentials, calls the underlying LizardFS operation, and normally destroys the context before returning.

Important APIs and types: Wrappers include lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir/rmdir/unlink, setattr, fsync, rename, symlink/readlink/link, chunk info, ACL get/set, and byte-range lock get/set. All accept `liz_t *instance` and `struct user_cred *cred` plus operation-specific LizardFS types.

Control flow: The standard pattern is `lzfs_fsal_create_context(instance, cred)`, return error/null if it fails, call `liz_*`, destroy context, and return the result. This centralizes credential translation for the rest of the FSAL and keeps handle/export code from managing LizardFS contexts directly.

State and persistence: The wrappers do not own persistent state. They create short-lived contexts and delegate all filesystem state to the LizardFS client instance. Calls with `cred == NULL` are used by pNFS DS paths to create root-like/local contexts via `lzfs_fsal_create_context()`.

Dependencies and integration: Depends on `context_wrap.h`, `lzfs_internal.h`, and the LizardFS C API. Used heavily by `handle.c`, `export.c`, `ds.c`, `mds_export.c`, `mds_handle.c`, and ACL conversion code.

Risks: `liz_cred_getlk()` creates a context but does not call `liz_destroy_context(ctx)` before returning, which leaks per-lock-test contexts. Because wrappers return `-1` or `NULL` without setting a LizardFS error when context creation fails, callers using `liz_last_err()` may report stale errors. Repetitive create/destroy can be expensive under high I/O and lock rates.

Test signals: Leak-test repeated lock tests, failure-inject context creation, validate credential mapping for normal users, anonymous users, and supplemental groups, and compare direct LizardFS error codes with FSAL error translation after wrapper failures.
