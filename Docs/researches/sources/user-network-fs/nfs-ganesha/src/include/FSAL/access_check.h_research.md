<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h

## Purpose
`FSAL/access_check.h` declares common FSAL access-check, credential switching, and ACL debug helpers. It is the shared interface for default permission evaluation across FSAL object handles.

## Important APIs, types, and functions
- `fsal_test_access()` checks requested FSAL access flags on an object and can report allowed and denied masks, with an `owner_skip` option.
- `display_fsal_v4mask()` formats an NFSv4 ACE permission mask into a display buffer.
- `fsal_set_credentials()` and `fsal_restore_ganesha_credentials()` are available when Ganesha can host local filesystems.
- `fsal_set_credentials_only_one_user()` and `fsal_save_ganesha_credentials()` support credential-switching policy and saved server credentials.
- `fsal_print_ace_int()` and `fsal_print_acl_int()` implement debug printing, with `fsal_print_ace` and `fsal_print_acl` macros injecting file, line, and function.

## Control flow
FSAL and protocol code call `fsal_test_access()` before operations that require permission checks. Local filesystem FSALs can switch process credentials around POSIX operations, then restore Ganesha credentials. Debug macros pass call-site metadata to ACL/ACE printers.

## State and persistence
The header itself has no state. Credential helpers affect process or thread credential state in their implementation, so callers must pair set/restore operations carefully. Access decisions are derived from object metadata, ACLs, and supplied credentials rather than persisted here.

## Dependencies and integration points
It depends on POSIX stat headers, `config.h`, `fsal_api.h`, log component types, display buffers, `fsal_ace_t`, and `fsal_acl_t`. It integrates FSAL modules with common permission enforcement and diagnostics.

## Risks
- Credential switching is high risk in multithreaded code if implementation scope is process-wide rather than thread-local on a platform.
- Callers that ignore `allowed` or `denied` outputs lose useful diagnostics for NFS access replies.
- `owner_skip` changes semantics and must match NFS owner-permission rules.
- Debug macros cast string literals and predefined macros to `char *`, which relies on callees not modifying them.

## Test signals
- Permission tests should compare mode-bit and ACL access decisions for owner, group, everyone, deny ACEs, and directory-specific masks.
- Credential tests should verify set/restore pairing and behavior when only-one-user restrictions apply.
- Debug output tests should format representative ACE and ACL masks.
- Local-FS builds with and without `GSH_CAN_HOST_LOCAL_FS` should compile cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h -->
