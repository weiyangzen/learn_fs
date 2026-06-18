<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sam.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/sam.py

Purpose: `sam.py` is a large Samba AD DS integration test suite for SAM object behavior over `SamDB`/LDB. It validates Windows-compatible semantics for users, groups, computers, account-control flags, generated attributes, password state, SPN maintenance, protected objects, and exact LDAP/LDB error mapping.

Important APIs, types, and functions:
- Top-level option parsing uses `samba.getopt.SambaOptions`, `CredentialsOptions`, `SubunitOptions`, and `TestProgram`; the command line supplies a host path or LDAP target.
- The global `ldb = SamDB(host, credentials=creds, session_info=system_session(lp), lp=lp)` is the live directory connection shared by all tests.
- `SamTests.setUp()` records `self.ldb` and `self.base_dn`, then force-deletes fixed `ldaptest*` users, computers, groups, and a DN containing an escaped comma.
- Tests build LDB updates with `Message`, `MessageElement`, `Dn`, and `FLAG_MOD_ADD`/`FLAG_MOD_REPLACE`/`FLAG_MOD_DELETE`.
- Constants from `samba.dsdb` and `samba.dcerpc.security` define expected `userAccountControl`, `groupType`, `sAMAccountType`, and RID outcomes.
- `find_repl_meta_data()` scans unpacked `drsblobs.replPropertyMetaDataBlob` entries for password-related DRS attids used by the smart-card tests.

Control flow:
- Module setup parses options, enforces sealed gensec features, normalizes plain host arguments into `tdb://` or `ldap://`, opens the system-session `SamDB`, then lets `TestProgram` discover all `SamTests` methods.
- Each test mutates the live directory, searches back selected attributes with `SCOPE_BASE`, and asserts either successful normalized state or a specific `LdbError` code.
- `test_users_groups()` is the broadest group-membership flow: it creates groups, extracts their RIDs from `objectSID`, checks default `primaryGroupID` selection for users/workstations/DCs/RODCs, rejects invalid `sAMAccountName` and primary group changes, validates primary-vs-secondary membership transitions, SID-form member references, duplicate member handling, non-existent member errors, and escaped DN cleanup.
- `test_sam_attributes()`, `test_primary_group_token_constructed()`, and `test_tokenGroups()` cover protected SAM attributes, constructed `primaryGroupToken`, `canonicalName`, and `tokenGroups` behavior.
- `test_groupType()` exercises add and modify paths for security/distribution global, universal, and domain-local groups; it asserts `sAMAccountType` derivation and rejects invalid/builtin-local or illegal scope transitions.
- `test_pwdLastSet()` validates the special `pwdLastSet` protocol: only `0` and `-1` are accepted as client-settable values, `-1` maps to current time, delete/add combinations have AD-like outcomes, and `UF_PASSWORD_EXPIRED` is represented by `pwdLastSet == 0` rather than a persistent UAC bit.
- `test_ldap_bind_must_change_pwd()` creates a password-backed user, builds SASL and simple bind `Credentials`, then checks wrong-password versus must-change-password LDAP failures, including expected HResult/DSID/WERROR substrings and the `ERR_STRONG_AUTH_REQUIRED` escape for simple binds.
- The `test_userAccountControl_*` groups split user and computer add/modify combinations. They verify normalization of zero/disabled/password-not-required/lockout/expired flags, accepted transitions between normal and trust accounts, rejected temp-duplicate/interdomain/server/RODC combinations, derived `sAMAccountType`, and preservation of manually chosen primary groups when account type does not change.
- `test_smartcard_required1/2/3()` check `UF_SMARTCARD_REQUIRED` side effects on key version number and replication metadata for `pwdLastSet`, password hashes, password histories, and supplemental credentials under accounts with and without an existing password.
- `test_isCriticalSystemObject_user()` and `test_isCriticalSystemObject()` assert how computer account roles, RODC flags, server trust flags, and account-type transitions drive or preserve `isCriticalSystemObject`.
- `test_service_principal_name_updates()` and `test_service_principal_name_uniqueness()` validate automatic HOST SPN rewriting from `dNSHostName` and `sAMAccountName`, ordering-sensitive combined modify semantics, duplicate-value handling, deletion behavior, and cross-object uniqueness.
- The final tests cover multi-valued `description` semantics on SAM objects, `fSMORoleOwner` restrictions to valid `nTDSDSA` DNs, protection against deleting RID < 1000 well-known objects while allowing rename/rename-back, and the complete default attribute set for a newly added user.

State and persistence behavior:
- Tests operate against a real Samba directory backend, not mocks. Adds, modifies, deletes, renames, password updates, metadata updates, and bind attempts persist until cleanup.
- Cleanup is mostly per-test via `setUp()` and targeted `delete_force()` calls. Because fixed names are reused, failed cleanup can affect later tests or subsequent runs.
- Directory-generated state under test includes `objectSid`, RIDs, `primaryGroupID`, `member`, `sAMAccountType`, `userAccountControl`, `pwdLastSet`, `lockoutTime`, `msDS-KeyVersionNumber`, `replPropertyMetaData`, `tokenGroups`, `primaryGroupToken`, `isCriticalSystemObject`, `servicePrincipalName`, and creation/change metadata.
- Some assertions intentionally allow environment variance, such as RODC primary group fallback and simple-bind rejection when strong auth is required.

Dependencies and integration points:
- Depends on Samba Python bindings (`samba`, `samba.samdb.SamDB`, `samba.credentials`, `samba.dsdb`, `samba.dcerpc.*`, `samba.tests.delete_force`) and Python LDB bindings.
- Exercises DSDB modules responsible for SAM name uniqueness, object-class/account-type validation, group membership maintenance, generated attributes, password and key material metadata, SPN update logic, FSMO owner validation, and protected-object deletion policy.
- Integrates with the Samba selftest/subunit harness through `samba.tests.subunitrun.TestProgram`.
- Requires credentials with enough directory rights to create, modify, delete, and rename users, computers, groups, and selected well-known objects; LDAP bind subtests also depend on server authentication policy.

Risks:
- The tests mutate live directory objects and well-known groups; they must run only in disposable test domains or isolated TDB backends.
- Fixed object names make concurrent runs against the same domain unsafe.
- Many assertions pin exact AD-compatible error codes and some diagnostic substrings; legitimate server-side error-message formatting changes can break tests even if high-level behavior remains correct.
- Time-sensitive `pwdLastSet` checks use `time.sleep(0.2)` and compare generated timestamps, so very slow or unusual time behavior can expose flakiness.
- Several behaviors depend on domain functional level or security policy, especially RODC defaults and simple bind strong-auth requirements.
- Because the module uses a global `ldb`, tests assume a single initialized connection and are not structured for independent import or parallelized method execution.

Test signals:
- Passing tests signal compatibility for core SAM object invariants: protected attributes cannot be removed, derived account/group attributes match UAC/groupType, primary group membership is maintained correctly, and generated attributes appear only when requested and applicable.
- Negative-path assertions are important signals: expected `ERR_ENTRY_ALREADY_EXISTS`, `ERR_UNWILLING_TO_PERFORM`, `ERR_OBJECT_CLASS_VIOLATION`, `ERR_CONSTRAINT_VIOLATION`, `ERR_INSUFFICIENT_ACCESS_RIGHTS`, `ERR_INVALID_CREDENTIALS`, `ERR_STRONG_AUTH_REQUIRED`, and related codes encode Windows behavior contracts.
- Password and smart-card tests signal correct coordination between user-visible account state and replicated secret metadata.
- SPN tests signal that automatic HOST SPN rewrite logic handles case-only changes, explicit SPN modifications, attribute deletion, multi-valued SPNs, and uniqueness constraints.
- The default-user test is a regression sentinel for the full initial attribute surface of new user objects, with volatile generated values explicitly skipped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sam.py -->
