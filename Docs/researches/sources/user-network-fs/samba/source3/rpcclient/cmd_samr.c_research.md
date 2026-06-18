# sources/user-network-fs/samba/source3/rpcclient/cmd_samr.c

## Purpose
`cmd_samr.c` implements the `rpcclient` SAMR command set. It exposes administrative and diagnostic operations for users, groups, aliases, domain information, display enumeration, SID/RID/name lookup, security descriptors, password policy, password changes, account creation/deletion, and setting user password information through multiple SAMR info levels.

## Important APIs, types, and functions
- `static struct dom_sid domain_sid` caches the first non-builtin domain SID discovered by `rpccli_try_samr_connects()`.
- `rpccli_try_samr_connects()` opens a SAMR connect handle using `dcerpc_try_samr_connects()`, enumerates domains, skips `builtin`, looks up the selected domain SID, and caches it globally.
- `get_domain_handle()` opens either the cached domain SID or `global_sid_Builtin` based on a `domain|builtin` argument.
- Display helpers format `samr_UserInfo*`, `samr_DomainInfo*`, `samr_DispEntry*`, password property flags, and group/alias information.
- Query/enumeration commands include `queryuser`, `querygroup`, `queryusergroups`, `queryuseraliases`, `querygroupmem`, `enumdomusers`, `enumdomgroups`, `enumalsgroups`, `enumdomains`, `querydispinfo*`, `querydominfo`, `queryaliasmem`, `queryaliasinfo`, `samquerysecobj`, `getdompwinfo`, `getusrdompwinfo`, `lookupdomain`, and `getdispinfoidx`.
- Mutating commands include `createdomuser`, `createdomgroup`, `createdomalias`, `deletedomgroup`, `deletedomuser`, `deletealias`, `chgpasswd*`, `setuserinfo`, and `setuserinfo2`.
- Password-setting support uses `nt_lm_owf_gen()`, `sess_crypt_blob()`, `init_samr_CryptPassword()`, `init_samr_CryptPasswordEx()`, and `init_samr_CryptPasswordAES()` for info levels 18, 21, 23, 24, 25, 26, and 31.
- The exported `samr_commands[]` table maps the SAMR user command names to `RPC_RTYPE_NTSTATUS` handlers with `&ndr_table_samr`.

## Control flow
Almost every command first calls `rpccli_try_samr_connects()` to establish a SAMR connect handle and initialize `domain_sid`. Commands then open a domain handle, optionally open a user/group/alias handle, call the relevant generated SAMR RPC, print formatted output, and close handles. Lookup commands validate returned counts to guard against malformed server responses. Enumeration commands use resume indexes and loop while the server returns `STATUS_MORE_ENTRIES`.

User and alias commands often accept either numeric RIDs or names. Some paths attempt a numeric open first, then fall back to `samr_LookupNames()` when opening RID zero fails or when the parsed RID is zero. Password change wrappers call higher-level `rpccli_samr_chgpasswd_user*()` helpers, while `chgpasswd4` directly calls the generated `dcerpc_samr_chgpasswd_user4()` server-name form. `setuserinfo` and `setuserinfo2` build the requested `union samr_UserInfo` variant, encrypt password material with the session key, resolve the target user, and invoke either `samr_SetUserInfo` or `samr_SetUserInfo2`.

## State and persistence behavior
The global `domain_sid` persists for the rpcclient process after first discovery and influences all later domain-scoped commands. The file otherwise stores no local persistent data. Remote SAM state is changed by create/delete commands, password changes, and set-user-info commands. Query commands can reveal account metadata, logon counters, password policy, security descriptors, and membership. Talloc frames own temporary encrypted password buffers in `setuserinfo`.

## Dependencies and integration points
The module depends on generated `ndr_samr` stubs, `rpc_client/cli_samr.h`, `rpc_client/init_samr.h`, `rpc_client/init_lsa.h`, SID/security helpers, string-to-integer helpers, session-key encryption, and rpcclient's command dispatcher. It uses common Samba constants for account flags, password properties, security descriptor selectors, and builtin/domain SIDs.

## Risks and edge cases
- The cached `domain_sid` assumes the first non-builtin domain is the desired target for the life of the process; multi-domain or retargeted sessions can surprise later commands.
- `cmd_samr_chgpasswd()` and `cmd_samr_chgpasswd2()` check `argc < 3` but then read `argv[3]`; they should require at least four arguments.
- `cmd_samr_query_aliasinfo()` allows at most four arguments but reads `argv[4]` when `argc > 3`, an out-of-bounds access for the documented optional access mask.
- `cmd_samr_get_dom_pwinfo()` allows `argc < 1` but unconditionally reads `argv[1]`; invoking without a domain can read past arguments.
- Passwords are supplied on the command line for `chgpasswd*` and `setuserinfo*`, exposing them through shell history and process inspection.
- Some close calls are skipped on early `goto done` paths unless guarded later, so remote handles may remain until connection teardown.
- `setuserinfo` includes low-level password hash/encryption handling; mistakes in level selection, session-key availability, salt, or buffer sizes can corrupt password updates or fail with policy errors.
- Commands that delete users, groups, and aliases perform permanent remote mutations with minimal confirmation.

## Test signals
Tests should cover domain SID discovery, builtin versus domain handle selection, name/RID lookup round trips, enumeration pagination, display info variants, query user by RID and by name fallback, security descriptor queries, and password policy display. Negative tests should call malformed argument combinations for `chgpasswd`, `chgpasswd2`, `queryaliasinfo`, and `getdompwinfo` under sanitizers. Mutation tests should run in an isolated SAM database and verify create/delete user/group/alias, password-change failure reporting, and `setuserinfo` levels 23/24/25/26/31 against known expected server behavior.
