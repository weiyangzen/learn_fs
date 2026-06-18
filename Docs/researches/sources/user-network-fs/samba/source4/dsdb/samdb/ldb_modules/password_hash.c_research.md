# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/password_hash.c

## Purpose

`password_hash.c` implements Samba AD DS's `password_hash` LDB module. It intercepts add and modify requests for password-bearing account objects, validates password operation semantics, applies domain and fine-grained password policy, derives all persisted password material, and rewrites the request into internal updates for `unicodePwd`, `dBCSPwd`, `ntPwdHistory`, `lmPwdHistory`, `supplementalCredentials`, and `pwdLastSet`.

The module bridges LDAP-facing password attributes (`unicodePwd`, `userPassword`, `clearTextPassword`, `dBCSPwd`) and internal AD storage. It understands the distinction between a user password change and an administrative reset, honors Samba-specific controls, enforces encrypted LDAP password modification, and emits status/audit side effects. It sits after ACL/samldb in the Samba DSDB module stack and before replication metadata/objectclass attribute processing, so its generated password fields become the authoritative values that later modules persist and replicate.

## Important APIs, Types, And Functions

Core request state is held in `struct ph_context`. It tracks the LDB module/request, asynchronous domain/PSO/self-search replies, the derived update message, password status and change controls, configured `password hash gpg key ids`, configured `password hash userPassword schemes`, and flags such as `pwd_reset`, `hash_values`, `update_password`, `smartcard_reset`, `pwd_last_set_bypass`, and `kdc_reset_smartcard_account_password`.

Password transformation state is held in `struct setup_password_fields_io`. It records account metadata (`userAccountControl`, `pwdLastSet`, `sAMAccountName`, UPN, SID, krbtgt detection, whether to store the NT hash), new and old supplied credentials, existing stored credentials and Kerberos key material, and generated outputs. Generated outputs include NT hash/history, salt, AES and DES Kerberos keys, supplementalCredentials blob, and final `pwdLastSet`.

Request entry points are `password_hash_add()`, `password_hash_modify()`, `password_hash_module_init()`, and exported `ldb_password_hash_module_init()`. `password_hash_needed()` is the shared gate that decides whether processing is needed, handles `DSDB_CONTROL_BYPASS_PASSWORD_HASH_OID`, rejects direct manipulation of password history and supplemental credentials, initializes `ph_context`, applies controls, and creates `ac->update_msg` with original password attributes stripped.

Password material generation is split into helpers:

- `setup_given_passwords()` converts UTF-8/UTF-16 cleartext forms and computes MD4 NT hashes.
- `setup_kerberos_key_hash()` computes an AES256 key for supplied old/new cleartext against the old salt for verification/history comparison.
- `setup_kerberos_keys()` derives the new Kerberos salt and AES keys and creates random DES key placeholders.
- `setup_nt_fields()` chooses whether to persist the NT hash and builds NT password history.
- `setup_primary_kerberos()` and `setup_primary_kerberos_newer()` build the older DES-only and newer AES/DES Kerberos supplemental packages while carrying forward old key slots.
- `setup_primary_wdigest()` builds the WDigest package when weak crypto is allowed.
- `setup_primary_userPassword()` and `setup_primary_userPassword_hash()` build configured `{CRYPT}` SHA-crypt userPassword supplemental hashes.
- `setup_primary_samba_gpg()` optionally encrypts cleartext UTF-16 into a SambaGPG supplemental package when GPGME is enabled and keys are configured.
- `setup_supplemental_field()` assembles `Primary:Kerberos-Newer-Keys`, `Primary:Kerberos`, `Primary:WDigest`, `Primary:CLEARTEXT`, `Primary:userPassword`, `Primary:SambaGPG`, and `Packages` into one NDR `supplementalCredentials` value.

Policy and final update helpers include `setup_last_set_field()`, `setup_password_fields()`, `setup_smartcard_reset()`, `check_password_restrictions()`, `check_password_restrictions_and_log()`, `make_error_and_update_badPwdCount()`, and `update_final_msg()`.

Parsing/control helpers include `msg_find_old_and_new_pwd_val()`, `setup_io()`, `ph_init_context()`, `ph_apply_controls()`, `get_domain_data_callback()`, `build_domain_data_request()`, `get_pso_data_callback()`, and `build_pso_data_request()`.

## Control Flow

For add requests, `password_hash_add()` calls `password_hash_needed()`. If no password, `pwdLastSet`, or relevant UAC smart-card control is present, the request passes through. If processing is needed, non-user/non-inetOrgPerson objects pass through except `clearTextPassword` is rejected. Valid account adds perform a base search of the domain object via `build_domain_data_request()`. When `get_domain_data_callback()` receives the domain policy and done reply, it calls `password_hash_add_do_add()`, which initializes setup state from the client add message, generates/validates fields, logs LDAP password-change outcomes where applicable, applies smart-card reset state, populates `ac->update_msg`, and sends a rewritten add request downstream with `ph_op_callback()`.

For modify requests, `password_hash_modify()` first calls `password_hash_needed()`. It then separates password operations from all other attribute modifications. Non-password modifications are sent downstream first through a modified request and `ph_modify_callback()`. After that succeeds, or if no other modifications existed, `password_hash_mod_search_self()` rereads the target object. `ph_mod_search_callback()` validates object class and stores the base-search result, then queries domain policy. Domain callback optionally follows `msDS-ResultantPSO` through `build_pso_data_request()` so fine-grained password policy can override domain defaults. Finally `password_hash_mod_do_mod()` initializes from the client message plus existing object, generates/validates derived fields, and sends the final forced metadata password modify.

Operation semantics are intentionally strict. `msg_find_old_and_new_pwd_val()` identifies old values from delete elements and new values from add/replace elements. A password change is represented by one delete and one add; a reset is represented by replace or add-without-delete. `password_hash_modify()` rejects mixed change/reset forms, duplicate add/delete operations, and malformed multi-valued password attribute operations. `setup_io()` further rejects mixed cleartext/hash input forms, simultaneous UTF-8 and UTF-16 password values, direct NT hash writes without `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID`, LM hash changes, deleting passwords, and inconsistent old-password mechanisms.

`check_password_restrictions()` runs after generated key material exists. It refuses unencrypted LDAP password modification when DSDB's encrypted-connection opaque says the connection is not encrypted. It verifies old-password knowledge for user changes unless a trusted control already proved it. It updates badPwdCount in its own transaction when the old password is wrong. It applies min age, complexity/length via `samdb_check_password()`, current password/history reuse checks using AES and NT history, old Kerberos key history checks by kvno, domain "refuse password change", and `UF_PASSWD_CANT_CHANGE`. Resets can skip some restrictions unless policy hints request reset-as-change behavior.

## State And Persistence Behavior

The module persists derived password state by rewriting LDB add/modify messages rather than writing directly to storage. `update_final_msg()` forces metadata updates for password attributes by adding empty elements with `DSDB_FLAG_INTERNAL_FORCE_META_DATA`, then fills generated values. On password update it always empties `dBCSPwd` and `lmPwdHistory`, reflecting Samba's no-LM-hash behavior. It stores `unicodePwd` only if `io->g.nt_hash` exists; NT hash persistence depends on `nt hash store` policy but is forced for non-normal accounts because machine/trust style flows need NETLOGON behavior. It stores `ntPwdHistory` when configured and enough material exists.

`supplementalCredentials` is regenerated from cleartext input, including Kerberos packages and optional weak/cleartext/GPG/userPassword packages. Functional level controls whether AES "newer keys" are produced. The old supplemental blob is parsed to preserve old/older Kerberos key slots where possible. The `Primary:SambaGPG` package is intentionally last when generated because package ordering is used as a current-password signal.

`pwdLastSet` is limited to `0` or `-1` unless bypass control is used. `-1` is replaced by the current DSDB/GMSA time. Adds always store the value. Modifies avoid no-op updates when appropriate. Setting `UF_SMARTCARD_REQUIRED` can suppress implicit `pwdLastSet` changes until the generated random password update is enabled by `setup_smartcard_reset()`.

Bad-password lockout state is a special side effect. On old-password mismatch, `make_error_and_update_badPwdCount()` aborts the current transaction, starts a short transaction to reread the account by GUID and call `dsdb_update_bad_pwd_count()`, closes it, and reopens the outer transaction so the failure returned to callers does not roll back the badPwdCount update.

## Dependencies And Integration Points

The module depends on LDB module APIs, DSDB/SAMDB helpers, Samba loadparm, security SID helpers, Heimdal/MIT Kerberos wrappers, GnuTLS hashing, MD4, generated NDR structures for supplemental credential packages, optional GPGME, auth logging, messaging, and KDC glue helpers.

Important controls are `DSDB_CONTROL_BYPASS_PASSWORD_HASH_OID`, `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID`, `DSDB_CONTROL_PASSWORD_CHANGE_STATUS_OID`, `DSDB_CONTROL_PASSWORD_CHANGE_OLD_PW_CHECKED_OID`, `DSDB_CONTROL_PASSWORD_BYPASS_LAST_SET_OID`, `DSDB_CONTROL_PASSWORD_DEFAULT_LAST_SET_OID`, `DSDB_CONTROL_PASSWORD_USER_ACCOUNT_CONTROL_OID`, `DSDB_CONTROL_PASSWORD_KDC_RESET_SMARTCARD_ACCOUNT_PASSWORD`, `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID`, `DSDB_CONTROL_RESTORE_TOMBSTONE_OID`, and policy hints OIDs. `password_hash_module_init()` registers the policy hints controls.

The `DSDB_PASSWORD_ATTRIBUTES` macro from `source4/dsdb/common/util.h` defines the password-facing attributes consumed here: `userPassword`, `clearTextPassword`, `unicodePwd`, and `dBCSPwd`. `samba_dsdb.c` places `password_hash` after `samldb` and before `instancetype`/`objectclass_attrs`. The ACL module validates password access and can pass reset/change classification through `DSDB_CONTROL_PASSWORD_ACL_VALIDATION_OID`.

The `dsdb/common/util.c` password-setting helpers use `DSDB_CONTROL_PASSWORD_HASH_VALUES_OID` and `DSDB_CONTROL_PASSWORD_CHANGE_STATUS_OID`, and DRS/import/pdb paths can use bypass controls. KDC and gMSA code reference the module's expectations for supplied random passwords for smart-card account reset/rollover paths.

## Risks And Edge Cases

This is a high-risk security module. Regressions can leak cleartext material, persist incompatible supplementalCredentials, weaken policy enforcement, break Kerberos/NTLM authentication, corrupt password history, or misclassify password reset/change authorization.

Notable edge cases include the heuristic that treats quoted UTF-16 `unicodePwd` as cleartext but unquoted 16-byte data as an NT hash when hash-values control is present; the comment acknowledges a very small collision possibility. Direct bypass accepts internally supplied hashes but performs extensive structural validation of histories and supplemental packages; any missed invariant could permit invalid replicated state. `parse_scheme()` checks SHA-crypt schemes and rounds, but its SHA-512 branch compares using `strlen(SHA_256_SCHEME)`, which is worth preserving tests around because it can affect scheme parsing. Configured userPassword scheme count is not bounded or uniqueness-checked.

The code mixes security policy, crypto derivation, and asynchronous LDB sequencing. Transaction manipulation for badPwdCount is intentionally unusual and error handling logs but preserves the original password failure. Smart-card and krbtgt randomization bypass user-supplied password material, so tests must ensure the final update really contains generated secrets and no stale history. GPGME support has build-time behavior differences and requires valid key IDs of at least 64 bits.

## Test Signals

Samba selftest explicitly lists `samba.tests.password_hash_gpgme`, `samba.tests.password_hash_fl2008`, `samba.tests.password_hash_fl2003`, and `samba.tests.password_hash_ldap`, covering GPG availability, functional-level differences, and LDAP WDigest/userPassword behavior. Broader password policy signals are in `source4/dsdb/tests/python/passwords.py`, including password change/reset constraints, max/min age commentary, NTLM-disabled knownfail cases, and LDAP password flows. ACL/password integration should also exercise `source4/dsdb/samdb/ldb_modules/acl.c` paths for password controls.

Regression tests should cover: add with and without initial password, modify split between non-password and password changes, replace vs delete/add classification, encrypted LDAP requirement, old-password mismatch and badPwdCount persistence, policy hints reset-as-change behavior, PSO overrides, NT hash store modes, krbtgt and RODC krbtgt random reset, smart-card required transition, functional level 2003 vs 2008 supplemental packages, weak crypto WDigest gating, configured userPassword SHA-crypt schemes and bad rounds, GPGME enabled/disabled, bypass validation of imported hashes, and `pwdLastSet` bypass/default controls.
