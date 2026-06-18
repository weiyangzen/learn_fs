# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_nt.c

## Purpose

`srv_samr_nt.c` is the main Samba source3 implementation of the SAMR RPC server entry points. It translates generated NDR SAMR operations into passdb, group mapping, account-policy, SID lookup, password-change, and security-descriptor operations. It owns server-side SAMR policy handles for connect, domain, user, group, and alias objects; maps requested generic access into object-specific rights; enforces privilege overrides such as `SeAddUsers` and `SeMachineAccount`; enumerates domain users/groups/aliases; queries and mutates user, group, alias, and domain policy state; and implements password-validation and password-change paths.

## Important APIs, Types, and Functions

- `enum samr_handle` and `struct samr_info`: private payloads stored behind policy handles. `samr_info` keeps `access_granted`, an object SID, and an optional `disp_info` enumeration cache pointer.
- `DISP_INFO`: per-domain display/enumeration cache with `pdb_search` handles for users, machines, groups, aliases, and masked user enumeration, plus a `tevent_timer` idle expiry.
- `create_samr_policy_handle()`, `samr_policy_handle_find()`, and `samr_handle_access_check()`: central handle lifecycle and access checking. `samr_policy_handle_find()` validates both handle type and required rights.
- `make_samr_object_sd()`: constructs default security descriptors with Everyone read/execute, Builtin Administrators and Account Operators full access, Domain Admins on DCs, and optional object-specific SID access.
- `_samr_Connect*()`, `_samr_OpenDomain()`, `_samr_OpenUser()`, `_samr_OpenGroup()`, `_samr_OpenAlias()`, `_samr_Close()`: policy-handle entry and object-open operations.
- `_samr_EnumDomainUsers()`, `_samr_EnumDomainGroups()`, `_samr_EnumDomainAliases()`, `_samr_QueryDisplayInfo*()`, `_samr_GetDisplayEnumerationIndex*()`: enumeration and display-info RPCs backed by passdb paged searches and `DISP_INFO`.
- `_samr_QueryUserInfo()` and `get_user_info_*()`: map passdb `struct samu` state into SAMR user information levels, with special handling for level 18 password hashes.
- `_samr_SetUserInfo()` and `set_user_info_*()`: update passdb fields and passwords for supported SAMR set-info levels, including RC4/session-key and AES-protected password formats.
- `_samr_QueryDomainInfo()`, `_samr_SetDomainInfo()`, `_samr_GetDomPwInfo()`: expose and update account policies such as password length/history/age, lockout duration/window, bad-attempt threshold, and force-logoff.
- `_samr_CreateUser2()`, `_samr_CreateDomainGroup()`, `_samr_CreateDomAlias()`, delete routines, and membership routines: create, delete, and mutate accounts/groups/aliases through passdb and group mapping APIs.
- `_samr_ChangePasswordUser2()`, `_samr_OemChangePasswordUser2()`, `_samr_ChangePasswordUser3()`, `_samr_ChangePasswordUser4()`: password-change variants. Older `_samr_ChangePasswordUser()` is intentionally not implemented.
- `_samr_ValidatePassword()`: DC-only, privacy-authenticated password validation for levels 2 and 3 using domain password policy and complexity checks.

## Control Flow

The typical SAMR flow starts with `_samr_Connect*()`, which checks pipe access, maps generic access, creates a connect handle, and stores granted rights. `_samr_LookupDomain()` or `_samr_EnumDomains()` resolves a domain SID. `_samr_OpenDomain()` validates the connect handle, checks a domain security descriptor and privilege overrides, rejects non-local and non-BUILTIN domains, attaches a `DISP_INFO` cache, and returns a domain handle.

Object-open calls compose or validate SIDs from domain handles. `_samr_OpenUser()` loads the target `samu` before final access decisions so it can require different privilege overrides for machine, normal, server-trust, and domain-trust accounts. `_samr_OpenGroup()` and `_samr_OpenAlias()` verify group/alias existence through group mapping, lookup, or `sid_to_gid()`, then create object handles with granted rights.

Enumeration calls obtain domain handles with enumeration rights, run passdb searches under `become_root()`, convert `samr_displayentry` rows into wire arrays, advance resume handles, and return `STATUS_MORE_ENTRIES` when the returned count reaches the local maximum. Display-info levels 1-5 share the same cache and differ only in account class and output structure.

Query paths allocate output unions on `p->mem_ctx`, load passdb data under root where required, clear password hashes from normal `samu` records with `samr_clear_sam_passwd()`, and call level-specific initializers. Level 18 is exceptional: it is only served over `NCALRPC` to a SYSTEM security token and deliberately avoids `become_root()`.

Set paths first derive the access mask from the requested information level or `fields_present`, validate the user handle, load the `samu`, enter a root block, and dispatch to level-specific setters. Attribute levels mostly call `copy_id*_to_sam_passwd()` from `srv_samr_util.c` and then `pdb_update_sam_account()`. Password levels decrypt or decode the password buffer first, set passdb plaintext/hash fields, optionally sync the UNIX password through `chgpasswd()`, and finally update passdb. Successful mutations flush the display cache for the affected SID.

Group and alias membership paths verify handle rights, call passdb membership APIs under root, return SAMR RID/SID arrays, and flush caches after mutations. Domain policy setters validate the information level and write passdb account policy keys.

## State and Persistence Behavior

Persistent state is primarily passdb-backed: user records (`pdb_create_user()`, `pdb_update_sam_account()`, `pdb_delete_user()`), domain groups and aliases (`pdb_create_dom_group()`, `pdb_delete_dom_group()`, `pdb_create_alias()`, `pdb_set_aliasinfo()`), group memberships (`pdb_add_groupmem()`, `pdb_del_groupmem()`), alias memberships (`pdb_add_aliasmem()`, `pdb_del_aliasmem()`), and account policies (`pdb_set_account_policy()`).

Transient state includes policy handles allocated with talloc on the pipe memory context and the static `DISP_INFO` caches for the local SAM and BUILTIN domains. Those caches can outlive a single SAMR handle and are expired by a tevent timer after `DISP_INFO_CACHE_TIMEOUT` seconds of idle time. Mutations call `force_flush_samr_cache()` to invalidate cached enumerations.

Privilege transitions are explicit. Most passdb reads/writes are bracketed by `become_root()` and `unbecome_root()`. Password-change paths also use transport encryption checks, session-key extraction, and cryptographic decoding before persistent updates. `_samr_ChangePasswordUser4()` uses a named mutex keyed by username when reloading account state and updating lockout counters, reducing races with concurrent bad-password tracking.

## Dependencies and Integration Points

This file integrates with generated SAMR NDR headers and the generated server compatibility include `ndr_samr_scompat.c`. Core dependencies include passdb (`struct samu`, account policies, searches, group mappings), security descriptors and access checking, privilege and security-token helpers, SID utilities, secrets for domain SID lookup, loadparm configuration, tsocket remote-address extraction, winbind toggling during account creation, base64 helpers for `munged_dial`, GnuTLS helpers for RC4 and AES password buffers, global tevent context, and password complexity/change helpers declared in `srv_samr_util.h`.

The RPC integration point is the `pipes_struct`/`dcesrv_call_state` environment. Memory ownership is mostly `p->mem_ctx`; server faults are signaled by setting `p->fault_state` for unsupported opnums and access-denied validation scenarios.

## Risks and Edge Cases

- Access control is broad and subtle. Root mode can override `samr_handle_access_check()`, and object opens apply privilege-based write grants. Regressions can expose account modification or password operations.
- Enumeration caching uses static pointers for BUILTIN and local SAM domains. Cache invalidation depends on mutation paths calling `force_flush_samr_cache()` with a SID that resolves to the same cache bucket.
- `can_create()` is explicitly racy because the passdb backend cannot be globally locked between lookup and create/rename.
- Password paths handle multiple legacy and modern formats. RC4/session-key handling is gated by weak-crypto policy and transport encryption for some levels, while AES levels rely on AEAD decrypt and length bounds. Missing a `data_blob_clear()` style cleanup can leak plaintext.
- `_samr_SetUserInfo()` performs many mutations inside a root block, including operations that can call UNIX password sync; failures midway can leave passdb and UNIX password state partially updated depending on backend semantics.
- Some SAMR operations are intentionally unimplemented and return RPC op-range faults. Compatibility-sensitive clients may rely on exact status/fault behavior.
- `_samr_RemoveMemberFromForeignDomain()` is effectively a no-op for the observed BUILTIN use case and warns for others; nested group behavior is noted as incomplete.
- Display-size calculations use fixed structure-size approximations for Windows compatibility rather than exact encoded sizes.

## Test Signals

Useful tests should exercise RPC-level access and status behavior: connect/open-domain rights, BUILTIN versus local SAM domain handling, user/group/alias enumeration with resume handles, display-info pagination and cache invalidation after mutations, object security query/set for password-change ACL behavior, user create/rename/delete paths, group and alias membership updates, account-policy query/set round trips, and unsupported opnum faults. Password tests should cover weak-crypto policy denial, RC4 info levels 23-26, AES info levels 31-32 and ChangePasswordUser4, complexity failures, min-length failures, bad-password counter updates, account lockout, trust-account UNIX-sync bypass, and plaintext cleanup where instrumentation exists.
