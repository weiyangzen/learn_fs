# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_acl.c

Purpose: this file converts ACLs between Ganesha FSAL/NFSv4 representation and SaunaFS ACL representation, then implements `getACL` and `setACL` wrappers for SaunaFS inode ACL operations.

Important functions: `convertFsalACLToSaunafsACL` creates a SaunaFS ACL from a mode and FSAL ACL, copying allow/deny ACEs, preserving low-byte flags, permissions, type, user/group ids, and translating FSAL special identities to SaunaFS special ids with `SAU_ACL_SPECIAL_WHO`. `convertSaunafsACLToFsalACL` allocates FSAL ACE data, pulls entries with `sau_get_acl_entry`, maps SaunaFS special identities back to `FSAL_ACE_SPECIAL_*`, and interns the ACL with `nfs4_acl_new_entry`. `getACL` releases an existing output ACL, calls `saunafs_getacl`, applies masks with `sau_acl_apply_masks(ownerId)`, converts to FSAL ACL, and destroys the SaunaFS ACL. `setACL` ignores NULL ACLs as success, converts FSAL ACLs to SaunaFS, calls `saunafs_setacl`, and destroys temporary SaunaFS ACLs.

Control flow and state: conversion is one-way allocation with explicit cleanup. `getACL` owns the old `*acl`, the temporary `sau_acl_t`, and the returned FSAL ACL reference. `setACL` owns only its temporary `sau_acl_t`. Error paths use `fsalLastError()` for SaunaFS failures and `ERR_FSAL_FAULT` for conversion/allocation failure.

Dependencies and integration points: depends on `context_wrap.h`, `saunafs_internal.h`, Ganesha FSAL ACL helpers/macros, `nfs4_ace_alloc`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and SaunaFS C API ACL calls. It uses `op_ctx->creds` and `SaunaFSExport::fsInstance`.

Risks: `convertSaunafsACLToFsalACL` asserts `sau_get_acl_entry` success and does not recover in non-debug builds beyond the API behavior. Only allow/deny ACEs are copied from FSAL to SaunaFS, so audit/alarm-like entries are dropped. The low-byte flag mask can discard higher FSAL flag bits except the explicit special-id marker. Conversion validity depends on FSAL macros interpreting group/special flags after `flag`/`iflag` fields are set.

Test signals: round-trip ACLs containing owner/group/everyone special ids, user ids, group ids, allow and deny entries, inherited/group flags, empty ACLs, NULL ACLs, invalid special ids, and SaunaFS get/set failures. Confirm existing output ACL references are released before replacement.
