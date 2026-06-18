# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.c

Purpose: this file provides shared SaunaFS FSAL helpers for credential context creation and error conversion.

Important functions: `createContext` converts a Ganesha `user_cred` into a SaunaFS `sau_context_t`. It maps anonymous uid/gid to root ids, creates a user context, prepends the primary gid to the secondary group array, and registers groups with `sau_update_groups`. `saunafsToNfs4Error` and `saunafsToFsalError` convert SaunaFS error codes through `sau_error_conv` into NFSv4 or FSAL errors, warning when no error was set and substituting `EINVAL`. `fsalLastError` and `nfs4LastError` read `sau_last_err()`.

Control flow and state: contexts are per-operation/per-credential and must be destroyed by callers. Secondary groups bind the context to a specific SaunaFS instance according to the C API contract. Error conversions preserve the native SaunaFS code as `fsal_status_t.minor`.

Dependencies and integration points: includes FSAL POSIX/NFS conversion helpers, `pnfs_utils.h`, and `saunafs_internal.h`. All SaunaFS wrappers should use these conversions rather than returning raw SaunaFS statuses.

Risks: `createContext` allocates `caller_glen + 1` gids but copies only `caller_glen` secondary entries after setting the primary gid; that is intentional but needs coverage. It uses `free(garray)` on memory allocated with `gsh_malloc`, which may be inconsistent if Ganesha memory wrappers require `gsh_free`. Failures from `sau_update_groups` are ignored, so callers may operate with incomplete group data.

Test signals: contexts for NULL creds, anonymous creds, normal creds, many secondary groups, failed context creation, and failed group update. Error tests should cover zero, known, and unknown SaunaFS error codes.
