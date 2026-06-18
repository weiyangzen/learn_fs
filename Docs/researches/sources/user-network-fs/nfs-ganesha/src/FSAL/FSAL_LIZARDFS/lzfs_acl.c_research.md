# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_acl.c

Purpose: Converts ACLs between Ganesha FSAL/NFSv4 representation and LizardFS ACL representation, and implements internal get/set ACL helpers for LizardFS handles.

Important APIs and types: Main functions are `lzfs_int_convert_fsal_acl()`, `lzfs_int_convert_lzfs_acl()`, `lzfs_int_getacl()`, and `lzfs_int_setacl()`. It uses `fsal_acl_t`, `fsal_ace_t`, `liz_acl_t`, `liz_acl_ace_t`, `nfs4_ace_alloc()`, `nfs4_acl_new_entry()`, and LizardFS ACL helpers. `lzfs_int_apply_masks()` is declared and called but defined elsewhere.

Control flow: FSAL-to-LizardFS conversion filters only ALLOW and DENY ACEs, maps flags, permissions, type, user/group ids, and special owner/group/everyone ids. LizardFS-to-FSAL conversion allocates an FSAL ACE array, reads each LizardFS ACL entry, maps flags and special ids, and interns the ACL through Ganesha's ACL cache. `getacl` releases any existing output ACL, fetches a LizardFS ACL, applies masks using owner id, converts it, destroys the LizardFS ACL, and returns FSAL status. `setacl` converts and calls `liz_cred_setacl()`.

State and persistence: No long-lived state is stored here. ACL persistence is in LizardFS. Ganesha ACL cache references are created/released through NFSv4 ACL helpers.

Dependencies and integration: Used by `handle.c` from `getattrs` and `setattr2`. Depends on `context_wrap`, `lzfs_internal`, LizardFS ACL API, Ganesha ACL macros, and `op_ctx->creds`.

Risks: The unused `count` variable in FSAL-to-LizardFS conversion suggests an earlier sizing design. Unsupported ACE types are silently skipped, which can weaken ACLs. In LizardFS-to-FSAL conversion, `iflag` is assigned instead of preserving group/user flag interactions beyond the low byte. Invalid special ids are logged and coerced. Mask application is external and must be correct for effective permissions.

Test signals: Round-trip ACLs with user, group, owner@, group@, everyone@, ALLOW/DENY, inherited flags, unsupported ACE types, empty ACLs, null ACL set, invalid special ids from server, and ACL cache reference leak checks.
