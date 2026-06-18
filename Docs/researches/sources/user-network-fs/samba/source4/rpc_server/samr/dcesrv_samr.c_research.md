# sources/user-network-fs/samba/source4/rpc_server/samr/dcesrv_samr.c

## Purpose

This file implements the Samba AD DC server side of the SAMR DCE/RPC interface. It maps SAMR policy handles to Samba `samdb`/LDB state, exposes domain, user, group, alias, display, password-policy, SID/RID lookup, and membership operations, and includes the generated NDR server dispatch table at the end. It is the central bridge between MS-SAMR wire operations and DSDB objects such as users, groups, builtin aliases, foreign security principals, password policy attributes, and account metadata.

## Important APIs, Types, And Functions

The file uses handle states declared in `dcesrv_samr.h`: `samr_connect_state`, `samr_domain_state`, `samr_account_state`, `samr_guid_cache`, and `enum samr_handle`. `dcesrv_samr_Connect*()` opens a SAM database context with caller credentials and returns a connect handle. `dcesrv_samr_OpenDomain()` converts a domain SID into a domain handle with domain DN, role, builtin flag, access mask, loadparm context, GUID caches, and the cached user enumeration array. `dcesrv_samr_OpenUser()`, `OpenGroup()`, and `OpenAlias()` resolve RID-derived SIDs to LDB records and create account handles.

Query and set helpers are macro-heavy. `QUERY_STRING`, `QUERY_UINT`, `QUERY_RID`, `QUERY_APASSC`, `QUERY_BPWDCT`, `QUERY_LHOURS`, and `QUERY_AFLAGS` translate LDB attributes into SAMR info unions. `SET_STRING`, `SET_UINT`, `SET_INT64`, `SET_UINT64`, `SET_AFLAGS`, `SET_LHOURS`, and `SET_PARAMETERS` build replace/delete modifications. Domain info helpers cover levels 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, and 13. User info support is broad: `QueryUserInfo` covers levels 1-17, 20, and 21, while `SetUserInfo` handles account fields and password reset levels 18, 21, 23-26, 31, and 32.

Important database helpers include `dcesrv_samdb_connect_as_user()`, `gendb_search()`, `gendb_search_dn()`, `samdb_search_domain()`, `dsdb_search()`, `dsdb_search_by_dn_guid()`, `dsdb_add_user()`, `dsdb_add_domain_group()`, `dsdb_add_domain_alias()`, `dsdb_lookup_rids()`, `dsdb_enum_group_mem()`, and `samdb_create_foreign_security_principal()`. Password updates are delegated to `samr_set_password()`, `samr_set_password_ex()`, `samr_set_password_buffers()`, and `samr_set_password_aes()` in `samr_password.c`.

## Control Flow

Most RPC operations start with `DCESRV_PULL_HANDLE()` to validate the incoming policy handle type and recover its state. Connect creates a `SAMR_HANDLE_CONNECT`; domain lookup and enumeration then operate on the connect state. `OpenDomain` searches by `objectSid`, determines primary vs BUILTIN domain behavior, initializes caches, and creates a `SAMR_HANDLE_DOMAIN`. Account open/create calls create `SAMR_HANDLE_USER`, `SAMR_HANDLE_GROUP`, or `SAMR_HANDLE_ALIAS` with a domain reference and account DN.

Domain query flow is a level switch selecting the minimal attribute list, an optional DN search, allocation of `union samr_DomainInfo`, and a second level switch that calls the level-specific filler. Domain set flow builds an LDB modify message for supported levels and calls `ldb_modify()`, with a local constraint check for lockout duration/window. Group and alias query/set flows are analogous but smaller, operating on `sAMAccountName`, `description`, and `numMembers`.

Enumeration has distinct paging strategies. `EnumDomainGroups` and `QueryDisplayInfo` cache sorted `objectGUID` values in `samr_guid_cache`, then page by resume/start index and re-read each object by GUID so deleted objects can be skipped without retaining full records. `EnumDomainUsers` instead builds and caches a sorted `samr_SamEntry` array of RID/name pairs on the domain handle; the comment notes this trades memory for faster winbind `getpwent` behavior. Alias enumeration does a direct search, sorts by RID, and resumes by last RID.

Membership calls convert between RIDs, SIDs, DNs, and group `member` values. Group member add/delete resolves the RID inside the domain before modifying `member`. Alias member add can create a foreign security principal when the SID is unknown. User group enumeration reads `primaryGroupID` and `memberOf` extended-DN SIDs, then returns primary plus domain global/universal groups. Display and lookup calls translate between names, RIDs, SIDs, and LSA SID types.

`SetUserInfo` starts an LDB transaction, builds attribute modifications according to the requested level and field mask, calls the password helper when a password field is present, applies `pwdLastSet` changes for expiration flags, then commits or cancels. AES password levels obtain the DCE/RPC transport session key before decrypting. `ValidatePassword` is restricted to TCP or local RPC with privacy auth level and checks complexity/minimum length through `samdb_check_password()`.

## State And Persistence

Persistent state is stored in Samba's SAM database through LDB modifications and DSDB helper calls. The code persists domain policy attributes, account attributes, user/group/alias objects, group memberships, foreign security principals, password hashes, and `pwdLastSet`. In-memory state is talloc-owned by DCE/RPC policy handles: connect handles own caller SAM contexts; domain handles own domain identity, caches, and references to the connect state; account handles own account DN/name/SID and a domain reference. Caches are per-domain-handle and are cleared when a new enumeration starts, when resume input is out of range, on some errors, or when enumeration completes. There is no standalone on-disk persistence outside LDB.

## Dependencies And Integration Points

The file integrates with generated `ndr_samr` RPC definitions, Samba DCE/RPC handle management, DSDB/SAMDB, LDB, LDAP NDR encoding, SID helpers, security descriptors, loadparm role/name settings, password policy helpers, and generated `ndr_samr_s.c` boilerplate. It also integrates behaviorally with winbind clients that depend on SAMR enumeration ordering, with LSA/SAM account type mappings, and with password helper code for encrypted reset buffers.

## Risks And Edge Cases

Access masks are mostly stored but not consistently enforced in this file; many security decisions are delegated to SAMDB/LDB ACLs or explicitly unimplemented with DCE/RPC faults. Enumeration caches can become stale while objects are deleted or modified; the code skips missing/invalid objects, but clients may see gaps or fewer returned entries than requested. `EnumDomainUsers` has a hazard if a nonzero resume handle is supplied without a populated cache; the intended call pattern starts at zero. Several paths assume unique SIDs and treat duplicates as internal corruption. `SetUserInfo` is high risk because field-mask handling, password update side effects, transaction cancellation, and `pwdLastSet` semantics must match Windows-compatible behavior. Some operations intentionally fault or return not supported, which is correct only if generated dispatch and client compatibility expectations align.

## Test Signals

Strong signals include Samba RPC tests for `samr_Connect*`, `LookupDomain`, `OpenDomain`, domain info levels, user/group/alias create/open/query/set/delete, RID/name lookup, paged user/group/display enumeration, membership add/remove including foreign SIDs, and password reset levels 18, 21, 23-26, 31, and 32. Regression tests should cover empty domains, deleted objects during paged enumeration, BUILTIN restrictions, duplicate/invalid SID handling, access-denied mapping from LDB, transaction rollback on password failures, privacy enforcement for `ValidatePassword`, and Windows-compatible sorting by RID.
