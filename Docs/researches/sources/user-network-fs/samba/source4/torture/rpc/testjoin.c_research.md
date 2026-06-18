# sources/user-network-fs/samba/source4/torture/rpc/testjoin.c

## Purpose

`testjoin.c` provides shared torture infrastructure for creating and deleting domain users or machine accounts used by RPC tests. It wraps SAMR and libnet domain join flows, creates credentials for temporary accounts, exposes account metadata, and provides privilege assignment helpers.

## Important APIs, Types, and Functions

`struct test_join` stores the SAMR pipe, user/domain policy handles, libnet join result, domain SID/names, user SID/GUID, and NetBIOS name. `torture_create_testuser_max_pwlen()` creates a normal or special SAMR account with a generated password, while `torture_create_testuser()` uses a 255-character maximum. `torture_join_domain()` creates a machine trust account through libnet and returns machine credentials. `torture_leave_domain()` deletes the account and, for AD DC joins, calls `torture_leave_ads_domain()` to remove server objects. `torture_setup_privs()` adds LSA rights to a SID. Accessors return the SAMR pipe, user policy handle, SIDs, GUID, and domain names.

## Control Flow

User creation connects to SAMR, locates the requested domain or enumerates domains to find the non-BUILTIN domain, opens it, creates or replaces the user, computes the user SID, queries password policy, generates a compliant password, encrypts it with the transport session key, and sets user info levels 24 and 21. Machine joins parse the binding, normalize transport to named pipes where appropriate, call `libnet_JoinDomain()` with `recreate_account = true`, copy output account/domain data into `test_join`, annotate the account through SAMR, and build `cli_credentials` with secure channel type based on account flags.

## State and Persistence Behavior

This file deliberately mutates domain state. It creates accounts, deletes pre-existing accounts with the same requested name, sets passwords and account flags, assigns descriptive fields, grants LSA rights, and deletes accounts during leave. If account creation fails partway, the failure path calls `torture_leave_domain()`. If the process exits before leave, accounts, rights, or AD server objects can remain.

## Dependencies and Integration Points

The file integrates generated SAMR and LSA stubs, libnet join APIs, Samba command-line credentials/loadparm, `init_samr_CryptPassword()`, transport session keys, LDB/LDAP cleanup for AD server objects, and security SID helpers. It is declared through `torture_rpc.h` and consumed by many RPC torture suites.

## Risks and Edge Cases

The helpers require powerful credentials and a working SAMR/LDAP path. `DeleteUser_byname()` deletes any existing object with the requested test name before retrying creation, so names must remain tightly scoped. Password generation depends on policy minimum length and the caller's maximum. `torture_leave_domain()` assumes `join->user_handle` is valid and logs but does not propagate delete failures. LSA rights added by `torture_setup_privs()` are not independently removed except through account deletion.

## Test Signals

Success is visible when downstream suites can authenticate with returned credentials, retrieve the expected SID/GUID/domain names, use the SAMR pipe and user handle, and cleanly delete accounts. Failure signals isolate to SAMR connect/open/create/set-info, session-key extraction, libnet join, LDAP cleanup, or insufficient privileges.
