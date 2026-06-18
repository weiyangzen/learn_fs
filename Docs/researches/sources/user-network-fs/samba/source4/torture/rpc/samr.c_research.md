# Research: sources/user-network-fs/samba/source4/torture/rpc/samr.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009989`: lines 1-8638, `Docs/researches/chunks/subset-b-009989_research.md`
- `subset-b-009990`: lines 8639-9474, `Docs/researches/chunks/subset-b-009990_research.md`

## Chunk Research

### subset-b-009989: lines 1-8638

# sources/user-network-fs/samba/source4/torture/rpc/samr.c lines 1-8638

## Scope

This chunk covers lines 1-8638 of `sources/user-network-fs/samba/source4/torture/rpc/samr.c`. It is the bulk of Samba's SAMR RPC torture test implementation: includes, shared constants, context type definitions, helpers for SAMR/LSA strings and password crypto buffers, most SAMR object tests for users/groups/aliases/domains, password-change test flows, bad-password and lockout policy tests, enumeration/display-info checks, and the beginning of the large-object stress helper.

The chunk stops inside `test_ManyObjects()`. Domain-open, connect, suite registration, and some wrappers begin after this chunk and are intentionally not described as if they were complete here.

## Purpose

The file exercises Microsoft SAMR server behavior through generated DCE/RPC client stubs and Samba's torture framework. This chunk validates that a server implements the expected semantics for:

- SAMR handle lifecycle, security descriptor query/set, shutdown and DSRM password endpoints.
- User, group, alias, and domain object creation, deletion, lookup, open, query, and mutation.
- User information class behavior across many SAMR info levels, including `SetUserInfo`, `SetUserInfo2`, `QueryUserInfo`, and `QueryUserInfo2`.
- Password setting and password changing through old LM/NT hash formats, RC4-encrypted SAMR password buffers, extended/confounded buffers, and newer AES password formats.
- Password policy effects on `pwdLastSet`, password history, password complexity/length, `badPwdCount`, and account lockout.
- Cross-protocol integration between SAMR, Netlogon, and LSA policy/account-rights state.
- Enumeration coherency between `EnumDomain*`, `LookupNames`, `LookupRids`, `QueryDisplayInfo*`, and domain counters.
- Large domain behavior by creating many users, groups, or aliases, then checking enumeration/display counts.

The tests are behavioral, not unit-local. They mutate a live test domain, compare observed `NTSTATUS` values with Windows-compatible expectations, and restore some domain policy state after invasive password tests.

## Important APIs, Types, And Helpers

The core context type in this chunk is `struct torture_samr_context`, which carries a SAMR connect handle, machine credentials for Netlogon-authenticated checks, an `enum torture_samr_choice` selector, and `num_objects_large_dc` for large-domain stress runs. `enum torture_samr_choice` controls whether created objects are only smoke-tested or receive password, attribute, privilege, bad-password, lockout, or many-object coverage.

Small initialization helpers populate generated NDR structures:

- `init_lsa_String()`, `init_lsa_StringLarge()`, and `init_lsa_BinaryString()` set string/binary fields expected by SAMR and LSA RPC calls.
- `samr_rand_pass_silent()`, `samr_rand_pass()`, `samr_very_rand_pass()`, and `samr_rand_pass_fixed_len()` generate passwords for policy-sensitive tests, including UTF-16 random-byte password blobs.

Common SAMR wrappers include:

- `test_samr_handle_Close()` for handle close assertions.
- `test_QuerySecurity()` and `test_SetSecurity()` for security descriptor round trips.
- `test_LookupName()` and `test_OpenUser_byname()` for name-to-RID-to-handle setup.
- `test_SetDomainInfo()`, `test_SetDomainInfo_ntstatus()`, and `test_QueryDomainInfo2_level()` for policy backup, mutation, and expected-error checks.

User information coverage is concentrated in `test_SetUserInfo()`, `test_QueryUserInfo()`, `test_QueryUserInfo2()`, and many password-specific setters:

- `test_SetUserPass()` tests level 24 RC4-style password setting.
- `test_SetUserPass_23()`, `_25()`, and `_32()` test field-present password levels and deliberately broken session keys/password buffers.
- `test_SetUserPass_31()` and `test_SetUserPassEx()` test AES and extended encrypted password info levels.
- `test_SetUserPass_18()` and `_21()` test hash-level updates, including session-key encryption of LM/NT hashes and invalid length rejection.
- `test_SetUserPass_level_ex()` is the generic backend used by the `pwdLastSet` matrix; it prepares levels 18, 21, 23, 24, 25, 26, 31, and 32 and can dispatch through either `SetUserInfo` or `SetUserInfo2`.

Password-change protocol coverage includes `test_ChangePasswordUser()`, `test_OemChangePasswordUser2()`, `test_ChangePasswordUser2()`, `test_ChangePasswordUser2_ntstatus()`, `test_ChangePasswordUser3()`, `test_ChangePasswordUser4()`, and `test_ChangePasswordRandomBytes()`. These build LM/NT hashes via `E_deshash()` and `E_md4hash()`, old/new password verifiers via `E_old_pw_hash()`, SAMR encrypted password buffers via `init_samr_CryptPassword*()`, and AES/PBKDF2 payloads via GnuTLS and Samba crypto helpers.

Object helpers cover aliases, users, groups, and domains:

- Alias helpers: `test_CreateAlias()`, `test_alias_ops()`, `test_QueryAliasInfo()`, `test_SetAliasInfo()`, `test_GetMembersInAlias()`, `test_AddMemberToAlias()`, `test_AddMultipleMembersToAlias()`, `test_GetAliasMembership()`, and delete-by-name/delete-handle variants.
- User helpers: `test_CreateUser()`, `test_CreateUser2()`, `test_user_ops()`, `test_OpenUser()`, `test_DeleteUser()`, and `test_DeleteUser_byname()`.
- Group helpers: `test_CreateDomainGroup()`, `test_QueryGroupInfo()`, `test_SetGroupInfo()`, `test_QueryGroupMember()`, `test_AddGroupMember()`, `test_OpenGroup()`, `test_DeleteDomainGroup()`, and `test_DeleteGroup_byname()`.
- Domain helpers: `test_QueryDomainInfo()`, `test_QueryDomainInfo2()`, `test_RidToSid()`, `test_GetBootKeyInformation()`, `test_TestPrivateFunctionsDomain()`, and `test_RemoveMemberFromForeignDomain()`.

Cross-protocol helpers are also important. `setup_schannel_netlogon_pipe()` binds Netlogon with schannel/sign/seal flags, while `test_SamLogon()` and `test_SamLogon_with_creds()` verify passwords through `netr_LogonSamLogonEx`. `test_DeleteUser_with_privs()` opens an LSA pipe, grants account rights to a user SID, deletes the SAMR user, then checks that LSA account-rights state persists until explicitly deleted.

## Control Flow

Most flows are organized around opening a domain handle, creating a temporary object, running selector-specific operations, and deleting the object unless the test intentionally transfers ownership to another cleanup path.

`test_user_ops()` is the main per-user dispatcher. It first resolves the test account RID, then switches on `enum torture_samr_choice`:

- `TORTURE_SAMR_USER_ATTRIBUTES` probes security, query levels, writable fields, password info, private functions, and a level-24 password set.
- `TORTURE_SAMR_PASSWORDS` runs machine-account password policy exceptions, field-present password-set levels 23/25/32, AES level 31, classic password changes, hash-level sets, and final query checks for expected account flags/RID.
- `TORTURE_SAMR_PASSWORDS_PWDLASTSET` enters the `test_SetPassword_pwdlastset()` matrix.
- `TORTURE_SAMR_PASSWORDS_BADPWDCOUNT` and `TORTURE_SAMR_PASSWORDS_LOCKOUT` enter domain-policy mutation wrappers that backup policies, run logon/password-change sequences, and restore policies.
- `TORTURE_SAMR_USER_PRIVILEGES` opens LSARPC and checks interaction between SAMR user deletion and LSA account rights.
- `TORTURE_SAMR_OTHER` and many-object selectors only require the account to exist.

`test_ChangePassword()` chains the major password-change entry points for one account: handle-bound `ChangePasswordUser`, server/account `ChangePasswordUser2`, LM-only OEM change, `ChangePasswordUser3` reject-reason checks for reused/simple/too-short/too-early passwords, two successful `ChangePasswordUser3` verifications, and the AES-based `ChangePasswordUser4` path.

`test_SetPassword_pwdlastset()` performs a nested matrix over password info levels, `fields_present` combinations, password-expired values, and query/set API variants. Each iteration sets a password, queries `pwdLastSet`, optionally verifies the new password through Netlogon, sleeps to avoid timestamp granularity issues, and checks when `pwdLastSet` should be zero, equal, or increasing. Samba3/Samba4 get a longer delay because of coarser timestamp granularity.

`test_Password_badpwdcount_wrap()` and `test_Password_lockout_wrap()` follow the same policy discipline: query original domain password and lockout policy, mutate them for the scenario, run enabled/disabled plus network/interactive credential cases, then restore original policy information. The bad-password path constructs password history and verifies when old passwords should or should not increment `badPwdCount`. The lockout path checks lockout threshold/duration validation, account lockout status via multiple `QueryUserInfo` levels, post-expiry unlock behavior, and `ChangePasswordUser2` behavior while locked.

Enumeration flows open or validate each enumerated object. `test_EnumDomainUsers_all()` iterates account-flag masks, checks mask filtering by reopening users and querying level 16, then tests reverse lookup with `LookupNames` and `LookupRids`. Group and alias enumeration helpers similarly open each returned RID. Display-info helpers page through `QueryDisplayInfo`, compare display rows with `QueryUserInfo` level 21, and check continuation/index behavior.

`test_ManyObjects()` begins at the end of this chunk. Within the covered lines it queries announced domain counts, creates `num_objects_large_dc` users/groups/aliases depending on `ctx->choice`, enumerates totals, and queries display info for users/groups. The cleanup/count assertions continue beyond line 8638.

## State And Persistence Behavior

These tests intentionally mutate server-side persistent account database state:

- Temporary users, groups, and aliases are created with fixed test prefixes such as `samrtorturetest`, `samrtorturetestgroup`, and `samrtorturetestalias`.
- Existing leftover test objects are deleted and recreated when `*_EXISTS` statuses are returned.
- User attributes such as names, comments, full names, profile/home paths, workstations, parameters, country/code page, expiry, logon hours, and account flags are changed and re-queried.
- Passwords are repeatedly reset and changed. The active password is tracked in a local `char **password` and verified through subsequent password-change calls and Netlogon logon attempts.
- Domain password and lockout policies are changed by some tests. Wrappers preserve `DomainPasswordInformation` and `DomainLockoutInformation` and restore them after their scenario loops.
- LSA account rights may outlive SAMR user deletion. `test_DeleteUser_with_privs()` explicitly validates this persistence and then removes the LSA account object.

Local state uses talloc contexts heavily. Per-user create loops allocate short-lived child contexts so generated NDR output and temporary strings can be released after each object. Policy handles are closed with `test_samr_handle_Close()` unless an RPC delete call consumes or clears the handle. The code checks `ndr_policy_handle_empty()` before deleting in some paths to avoid double use after helper operations.

Some tests are gated by torture settings because they are destructive or server-family-specific. `dangerous` is required for shutdown and the async enumeration stress test. Samba3/Samba4 settings skip or relax known-incompatible behavior around security descriptor setting, multi-member alias operations, group member attributes, and timestamp granularity. Builtin-domain SID checks expect create operations to be refused.

## Dependencies And Integration Points

This chunk depends on generated RPC/NDR interfaces for SAMR, LSA, and Netlogon: `dcerpc_samr_*_r`, `dcerpc_lsa_*_r`, and `dcerpc_netr_LogonSamLogonEx_r`. It also relies on Samba's torture framework assertions and reporting (`torture_assert*`, `torture_comment`, `torture_result`, `torture_skip`, `torture_fail`) to turn protocol responses into test outcomes.

Credential and authentication integration comes from `cli_credentials`, Netlogon schannel credentials, and DCE/RPC binding auth metadata. `test_SamLogon()` constructs either interactive password-logon data or NTLM network-logon responses, encrypts the Netlogon payload with the machine account credential state, and accepts either validation level 6 or a fallback to level 3.

Cryptographic dependencies are central:

- `E_md4hash()`, `E_deshash()`, and `mdfour()` produce NT, LM, or raw-byte password hashes.
- `E_old_pw_hash()` links old/new password hashes for verifier fields.
- `sess_crypt_blob()`, `samba_gnutls_arcfour_confounded_md5()`, and GnuTLS ARCFOUR encrypt legacy buffers.
- `init_samr_CryptPassword()`, `init_samr_CryptPasswordEx()`, and `init_samr_CryptPasswordAES()` build SAMR password info-level payloads.
- `gnutls_pbkdf2()` and `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()` build the `ChangePasswordUser4` AES payload.

Directory/security dependencies include `dom_sid_*` helpers for RID/SID construction and comparison, `global_sid_Builtin`, account flag constants such as `ACB_NORMAL`, `ACB_WSTRUST`, `ACB_DISABLED`, and domain policy constants such as `DomainPasswordInformation`, `DomainLockoutInformation`, and `DOMAIN_PASSWORD_COMPLEX`.

## Risks And Maintenance Notes

The tests are highly stateful and can leave domain policy or account objects changed if a hard failure exits before restore logic runs. The bad-password and lockout wrappers restore policies at the end, but they do not use a single structured cleanup block around every assertion. New assertions in those paths should be placed carefully or paired with cleanup-safe control flow.

Password tests rely on live policy timing, random password generation, and server-specific behavior. Min password age, password complexity, history length, timestamp granularity, and lockout windows can make failures environment-dependent. The code already accepts `NT_STATUS_PASSWORD_RESTRICTION` as non-fatal in some places and has Samba3/Samba4 conditionals; expanding coverage should preserve these compatibility allowances.

Several paths intentionally submit malformed cryptographic data and expect exact failures such as `NT_STATUS_WRONG_PASSWORD`, `NT_STATUS_INVALID_PARAMETER`, `NT_STATUS_ACCESS_DENIED`, or `NT_STATUS_ACCOUNT_LOCKED_OUT`. These are protocol-compatibility tests; changing expected statuses can mask regressions in Windows-compatible semantics.

Legacy LM/OEM password paths use weak algorithms because the protocol requires them. They should remain test-only and should not be copied into production authentication logic except through existing Samba protocol helpers.

Fixed test names create collision risk when previous runs fail. Most create helpers handle object-exists statuses by deleting stale objects, but concurrent test runs against the same domain can still interfere with one another. Large-object tests also stress enumeration counts and can be expensive or disruptive depending on `num_objects_large_dc`.

The chunk includes many server-family conditionals. Removing a skip or relaxing condition without testing against Windows, Samba3, Samba4 AD DC, and builtin-domain handles risks converting known differences into false regressions.

## Test Signals

Important positive signals from this chunk are:

- SAMR calls return transport `NT_STATUS_OK` and expected operation statuses for every queried/set info level.
- Created users, groups, and aliases have expected account flags, primary groups, RIDs, membership state, and deletion behavior.
- Password set/change methods produce passwords that work through subsequent `ChangePasswordUser3` or Netlogon checks.
- Deliberately broken password buffers return expected failure statuses and do not update local `password` state.
- `pwdLastSet` is zero when forced expired, nonzero and increasing after password updates, or unchanged for field-present updates that do not include a password or expired flag.
- `badPwdCount` increments, resets, or remains unchanged according to enabled/disabled state, interactive/network logon type, and password-history recency.
- Lockout state appears consistently across `QueryUserInfo` levels 3, 5, 16, and 21, and authentication returns `NT_STATUS_ACCOUNT_LOCKED_OUT` while the account is locked.
- `EnumDomainUsers`, `EnumDomainGroups`, `EnumDomainAliases`, `QueryDisplayInfo*`, `LookupNames`, and `LookupRids` remain coherent.
- LSA account rights remain after SAMR user deletion until the LSA account object is deleted.
- Large-object creation and enumeration counts increase by the expected number for the selected object type; final count assertions continue after this chunk boundary.

Useful regression indicators include unexpected `NT_STATUS_INVALID_INFO_CLASS` on supported levels, missing returned arrays with nonzero counts, display-info entries that disagree with `QueryUserInfo`, failure to restore domain policy, stale test objects that cannot be deleted, and password-policy failures that report the wrong extended reject reason.

## Chunk Boundary Notes

Lines 1-8638 define all helper families needed by later suite entry points, but this chunk does not include the final connect/open-domain orchestration or public torture suite registration functions. The merge lane should combine this document with later chunks before making whole-file claims about top-level test registration or the complete `test_ManyObjects()` cleanup and count-validation path.

### subset-b-009990: lines 8639-9474

# sources/user-network-fs/samba/source4/torture/rpc/samr.c lines 8639-9474

## Scope

This chunk is the final slice of Samba's SAMR RPC torture test source. It starts in the cleanup and count-check tail of `test_ManyObjects()` and then contains the domain-level test dispatcher, domain lookup/enumeration helpers, SAMR connect-version coverage, the `samr_ValidatePassword` test, and the public torture entry points/suite builders for the main SAMR, user, password, large-DC, and password-policy scenarios.

The surrounding declarations matter for this chunk: `struct torture_samr_context` carries the active SAMR connect handle, optional machine credentials, the selected `enum torture_samr_choice`, and the large-DC object count. The constants `TEST_ACCOUNT_NAME`, `TEST_ACCOUNT_NAME_PWD`, `TEST_ALIASNAME`, and `TEST_GROUPNAME` provide fixed object names for user/group/alias creation and cleanup.

## Purpose

The chunk wires many lower-level SAMR operation tests into executable torture flows. Each top-level function opens a DCERPC connection to `ndr_table_samr`, creates a context selecting one test family, connects to SAMR, enumerates domains, runs domain-specific checks, and closes the resulting handle.

The main behavioral themes are:

- Verifying SAMR connect procedure variants from `samr_Connect` through `samr_Connect5`.
- Enumerating SAM domains and proving that lookup, domain password info, and domain-open paths work for every advertised domain.
- Dispatching domain tests by selected scenario, including user creation/attributes/password behavior, large object enumeration, alias/group/member tests, domain info queries, display info, private functions, RID-to-SID conversion, and boot key info.
- Exercising handle lifetime behavior by opening a domain, closing the parent connect handle, running domain tests, and then reconnecting the parent handle.
- Creating and deleting temporary users, aliases, groups, and bulk objects, while treating Samba3 mode differently where some objects are only closed rather than deleted.
- Providing suite constructors for machine-backed tests that require BDC/machine credentials, including `pwdLastSet`, privileged-user deletion, bad-password count, and lockout cases.
- Testing `samr_ValidatePassword` as its own suite and skipping cleanly when the server lacks that RPC procedure.

## Important APIs, Types, And Functions

Key local functions in this chunk:

- `test_OpenDomain(struct dcerpc_pipe *p, struct torture_context *tctx, struct torture_samr_context *ctx, struct dom_sid *sid)`: opens a domain with `samr_OpenDomain`, closes the parent connect handle to test server reference counting, dispatches the selected test family, deletes any remaining test handles, closes the domain handle, and reconnects SAMR.
- `test_LookupDomain(...)`: validates `samr_LookupDomain` error semantics for a NULL domain name and a known-bad domain name, looks up a real domain name from enumeration, calls `test_GetDomPwInfo()`, and enters `test_OpenDomain()`.
- `test_EnumDomains(...)`: calls `samr_EnumDomains`, iterates `struct samr_SamArray` entries, calls `test_LookupDomain()` for each, and then repeats enumeration once more.
- `test_Connect(...)`: executes `samr_Connect`, `samr_Connect2`, `samr_Connect3`, `samr_Connect4`, and `samr_Connect5` in sequence, closing the previously successful handle whenever a newer variant succeeds. The last successful handle is returned through `*handle`.
- `test_samr_ValidatePassword(...)`: sends `samr_ValidatePassword` level `NetValidatePasswordReset` requests for several sample passwords against a deliberately non-existent account, reporting whether the server policy allowed or refused each password.
- Top-level tests: `torture_rpc_samr()`, `torture_rpc_samr_users()`, `torture_rpc_samr_passwords()`, `torture_rpc_samr_pwdlastset()`, `torture_rpc_samr_users_privileges_delete_user()`, `torture_rpc_samr_many_accounts()`, `torture_rpc_samr_many_groups()`, `torture_rpc_samr_many_aliases()`, `torture_rpc_samr_badpwdcount()`, and `torture_rpc_samr_lockout()`.
- Suite builders: `torture_rpc_samr_passwords_pwdlastset()`, `torture_rpc_samr_user_privileges()`, `torture_rpc_samr_large_dc()`, `torture_rpc_samr_passwords_badpwdcount()`, `torture_rpc_samr_passwords_lockout()`, and `torture_rpc_samr_passwords_validate()`.

Important generated RPC/NDR types used directly:

- `struct samr_OpenDomain`, `struct samr_LookupDomain`, `struct samr_EnumDomains`.
- `struct samr_Connect`, `samr_Connect2`, `samr_Connect3`, `samr_Connect4`, and `samr_Connect5`.
- `union samr_ConnectInfo`, used at connect level 1 with `client_version = 0` and `supported_features = 0`.
- `struct samr_ValidatePassword`, `union samr_ValidatePasswordReq`, and `union samr_ValidatePasswordRep`.
- `struct policy_handle`, `struct dom_sid`, `struct dom_sid2`, `struct lsa_String`, and `struct samr_SamArray`.

Important harness and utility APIs:

- `torture_rpc_connection()` opens a SAMR DCERPC pipe against `ndr_table_samr`.
- `torture_suite_create()`, `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_rpc_tcase_add_test()`, `torture_rpc_tcase_add_test_ex()`, and `torture_rpc_tcase_add_test_creds()` register test cases.
- `torture_assert_ntstatus_ok()`, `torture_assert_ntstatus_equal()`, `torture_assert()`, `torture_result()`, `torture_comment()`, and `torture_skip()` provide failure, skip, and diagnostic behavior.
- `talloc_zero()`, `talloc_get_type_abort()`, and `talloc_free()` manage context-owned state.
- `ndr_policy_handle_empty()` prevents delete calls on never-opened handles.

## Control Flow

The ordinary top-level SAMR flow is:

1. A public entry point such as `torture_rpc_samr()` calls `torture_rpc_connection(torture, &p, &ndr_table_samr)` and extracts `p->binding_handle`.
2. It allocates a `struct torture_samr_context` and sets `ctx->choice` to the requested scenario.
3. It calls `test_Connect()`, which probes connect procedure versions and leaves `ctx->handle` set to the newest successful connect handle.
4. Some broad tests query security first, except when the `samba3` torture setting is enabled.
5. `test_EnumDomains()` enumerates domains, calls `test_LookupDomain()` for every advertised domain, and reissues `EnumDomains` as a final sanity check.
6. `test_LookupDomain()` checks invalid-parameter and no-such-domain paths before resolving the real domain SID, obtaining domain password info, and calling `test_OpenDomain()`.
7. `test_OpenDomain()` opens the domain, closes `ctx->handle`, runs the selected domain test branch, cleans up created object handles, closes the domain handle, then reconnects `ctx->handle` with `test_Connect()`.
8. The top-level entry point may run dangerous-only shutdown/DSRM password probes and then closes `ctx->handle`.

`test_OpenDomain()` is the central dispatcher. Its switch on `ctx->choice` maps scenarios as follows:

- `TORTURE_SAMR_PASSWORDS` and `TORTURE_SAMR_USER_PRIVILEGES`: optionally run `test_CreateUser2()` outside Samba3 mode, then create a standard user through `test_CreateUser()`.
- `TORTURE_SAMR_USER_ATTRIBUTES`: does the same user creation and then requires `test_QueryDisplayInfo()` because the attribute test path needs richer users to validate display state.
- `TORTURE_SAMR_PASSWORDS_PWDLASTSET`, `TORTURE_SAMR_PASSWORDS_BADPWDCOUNT`, and `TORTURE_SAMR_PASSWORDS_LOCKOUT`: pass `ctx->machine_credentials` into `test_CreateUser2()`/`test_CreateUser()` so password policy state can be driven with machine-backed credentials.
- `TORTURE_SAMR_MANY_ACCOUNTS`, `TORTURE_SAMR_MANY_GROUPS`, and `TORTURE_SAMR_MANY_ALIASES`: call `test_ManyObjects()` to create, enumerate/display-query, and clean up a configurable number of objects.
- `TORTURE_SAMR_OTHER`: creates a baseline user and then runs a broad domain API sweep, including security query/set outside Samba3 mode, foreign-domain member removal, alias/group creation, alias membership, domain info variants, user/group/alias enumeration, async user enumeration, display-info variants and continuation, display enumeration index tests outside Samba4 mode, group list, private functions, RID-to-SID, and boot key info.

The visible tail of `test_ManyObjects()` handles cleanup after bulk object creation and enumeration. For Samba3-mode tests it closes every non-empty bulk handle. Otherwise it deletes users, groups, or aliases according to `ctx->choice`. It frees the handle array and, for the many-accounts case only, reports unexpected enumeration and display-info counts when the observed count is not the original domain count plus the number created.

The large-DC suite constructor creates one shared `torture_samr_context`, defaults `num_objects_large_dc` to `150`, and registers `many_aliases`, `many_groups`, and `many_accounts`. Each test updates the shared context choice and optionally overrides the object count from the `large_dc` torture setting before connecting and enumerating domains.

The password-policy suite constructors use `torture_suite_add_machine_bdc_rpc_iface_tcase()` with `TEST_ACCOUNT_NAME_PWD`, then register credential-aware callbacks. These callbacks all establish a fresh SAMR connection and store `machine_credentials` in `ctx` before domain enumeration dispatches into the corresponding password-state test branch.

## State And Persistence Behavior

This chunk does not define persistent storage, but it intentionally mutates server-side SAM database state during tests:

- `test_OpenDomain()` may create temporary users, aliases, and groups and then deletes them before returning.
- The bulk large-DC paths create many users, groups, or aliases using deterministic names derived from the test constants and a zero-padded index. They either delete them or, under Samba3 mode, only close handles.
- Password scenarios can change user password-related state such as password last set, bad password count, and lockout state through lower-level helpers invoked by `test_CreateUser()` and `test_CreateUser2()`.
- `test_SetDsrmPassword()` and `test_Shutdown()` are called by broad entry points, but they are guarded by the `dangerous` torture setting in their implementations. In normal runs they skip rather than changing dangerous machine state.

Handle state is a major part of the test:

- `test_Connect()` may open up to five SAMR connect handles but closes the previous handle whenever a later connect variant succeeds.
- `test_OpenDomain()` deliberately closes the main connect handle while retaining the domain handle. This verifies that the server keeps the domain object alive independently of the parent connection handle.
- At the end of each domain run, `test_OpenDomain()` closes object handles through delete helpers when they are not empty, closes the domain handle, and reconnects the main context handle so the outer enumeration loop can continue.

Memory lifetime is owned by the torture context or suite context through talloc. `test_ManyObjects()` frees its bulk handle array explicitly. The chunk relies on talloc cleanup for per-test contexts and generated RPC output buffers.

## Dependencies And Integration Points

Primary dependencies are Samba's generated SAMR client stubs from `librpc/gen_ndr/ndr_samr_c.h` and the DCERPC binding/pipe layer:

- `dcerpc_samr_OpenDomain_r`
- `dcerpc_samr_LookupDomain_r`
- `dcerpc_samr_EnumDomains_r`
- `dcerpc_samr_Connect_r`
- `dcerpc_samr_Connect2_r`
- `dcerpc_samr_Connect3_r`
- `dcerpc_samr_Connect4_r`
- `dcerpc_samr_Connect5_r`
- `dcerpc_samr_ValidatePassword_r`

The chunk depends heavily on earlier helpers in `samr.c`:

- Creation/deletion helpers: `test_CreateUser()`, `test_CreateUser2()`, `test_DeleteUser()`, `test_CreateAlias()`, `test_DeleteAlias()`, `test_CreateDomainGroup()`, `test_DeleteDomainGroup()`.
- Domain tests: `test_QuerySecurity()`, `test_RemoveMemberFromForeignDomain()`, `test_GetAliasMembership()`, `test_QueryDomainInfo()`, `test_QueryDomainInfo2()`, `test_EnumDomainUsers_all()`, `test_EnumDomainUsers_async()`, `test_EnumDomainGroups_all()`, `test_EnumDomainAliases_all()`, `test_QueryDisplayInfo()`, `test_QueryDisplayInfo2()`, `test_QueryDisplayInfo3()`, `test_QueryDisplayInfo_continue()`, `test_GetDisplayEnumerationIndex()`, `test_GetDisplayEnumerationIndex2()`, `test_GroupList()`, `test_TestPrivateFunctionsDomain()`, `test_RidToSid()`, and `test_GetBootKeyInformation()`.
- Bulk enumeration helpers: `test_EnumDomainUsers()`, `test_EnumDomainGroups()`, `test_EnumDomainAliases()`, and `test_QueryDisplayInfo_level()`.
- Setup/teardown helpers: `test_samr_handle_Close()`, `test_SetDsrmPassword()`, and `test_Shutdown()`.

Torture settings influence behavior:

- `samba3`: skips some `test_CreateUser2()` and security calls, and changes bulk cleanup from deletion to handle close in `test_ManyObjects()`.
- `samba4`: skips display enumeration index tests in the broad `SAMR-OTHER` path.
- `large_dc`: overrides the large-DC object count.
- `dangerous`: controls shutdown and DSRM password side-effect tests in helper functions called by this chunk.

The suite constructors are integration points for Samba's torture registry. The non-suite public functions (`torture_rpc_samr`, `torture_rpc_samr_users`, and `torture_rpc_samr_passwords`) are direct RPC torture entry points. The suite-returning functions create named suites that can be selected independently, especially for machine-credential-backed password behavior.

## Risks And Maintenance Notes

- `test_OpenDomain()` closes `ctx->handle` and later reconnects it. If any branch returns early after the close or if cleanup assertions abort, subsequent outer-domain enumeration state may be invalid. The current function mostly accumulates failures in `ret` and centralizes cleanup, which is important to preserve.
- The large-DC tests share a single `struct torture_samr_context` among three test registrations. Sequential torture execution makes this workable, but parallel execution of those tests would race on `ctx->choice`, `ctx->handle`, and `ctx->num_objects_large_dc`.
- `test_EnumDomains()` checks `if (!*r.out.sam)` after `r.out.sam = &sam`; this assumes the RPC stub initializes `sam`. A malformed server response with success but a NULL array returns false rather than asserting with a clear diagnostic.
- `test_ManyObjects()` only compares expected enumeration/display counts for the many-accounts path. Many-groups and many-aliases paths still validate RPC success, but not exact count deltas in this visible tail.
- The many-accounts count mismatch only logs comments and still returns true. This makes count drift diagnostic rather than a hard failure.
- The `samr_ValidatePassword` test only comments when transport is not `NCACN_IP_TCP`; it does not skip or fail solely on transport mismatch. The subsequent RPC result determines behavior.
- `test_samr_ValidatePassword()` assumes a non-NULL validation reply after successful RPC/result status. If a server returns success with a NULL reply pointer, the diagnostic dereference would be unsafe.
- `test_Connect()` closes previous handles without folding close failures into `ret`. A server that succeeds connects but mishandles close could be underreported by this specific function, though broader handle-close tests may catch it elsewhere.
- Several paths mutate real SAMR state. The deterministic object names reduce leak ambiguity, but failed cleanup can leave users, groups, or aliases behind and can affect later runs.
- The broad `TORTURE_SAMR_OTHER` path chains many tests with `ret &= ...`, so it continues after failures. This improves coverage per run but can make the first failing API harder to isolate without reading the emitted torture messages.

## Test Signals

Useful signals for this chunk include:

- `samr` should connect through at least one connect variant and leave a valid context handle after `test_Connect()`.
- `samr_Connect3`, `samr_Connect4`, and `samr_Connect5` failures are reported as explicit torture failures, while older connect failures are logged and reflected in the boolean result.
- `samr_EnumDomains` must return at least one `samr_SamArray` entry; each entry should survive lookup, password-info probing, domain open, branch-specific tests, and reconnect.
- Domain handle reference counting is validated when branch tests continue to work after the parent connect handle is closed.
- `LookupDomain(NULL)` should return `NT_STATUS_INVALID_PARAMETER`, and lookup of `"xxNODOMAINxx"` should return `NT_STATUS_NO_SUCH_DOMAIN`.
- The broad `SAMR-OTHER` run should cover user creation/deletion, alias/group creation/deletion, domain info, display info, enumeration, group/RID helpers, and boot key information, with Samba3/Samba4 settings changing only the documented skips.
- `samr.large-dc` should create and clean up the configured number of objects for aliases, groups, and accounts, defaulting to 150 when `large_dc` is unset.
- Password-policy suites should run under machine BDC RPC test cases and pass machine credentials into their branch-specific user operations.
- `samr.passwords.validate` should either skip on `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE` or return successful SAMR validation replies for all sample passwords, emitting allow/refuse status codes.
- Final cleanup should leave no non-empty created user, alias, group, domain, or connect handles unclosed in successful non-Samba3 paths.
