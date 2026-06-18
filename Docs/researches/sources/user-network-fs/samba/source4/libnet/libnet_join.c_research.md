# sources/user-network-fs/samba/source4/libnet/libnet_join.c

## Purpose
`libnet_join.c` implements domain join operations. It creates or reuses a machine/domain account over SAMR, sets its password and account flags, performs additional ADS/LDAP/DRSUAPI finishing for AD domains, and provides a convenience wrapper for joining the local machine as a member and storing local secrets.

## Important APIs, Types, And Functions
The main public functions are `libnet_JoinDomain()` and `libnet_Join_member()`. The important internal helper is `libnet_JoinADSDomain()`, called when `libnet_RpcConnect` discovered an AD realm.

`libnet_JoinDomain()` uses `libnet_RpcConnect` with `LIBNET_RPC_CONNECT_DC_INFO`, SAMR calls (`Connect`, `LookupDomain`, `OpenDomain`, `CreateUser2`, `LookupNames`, `OpenUser`, `DeleteUser`, `QueryUserInfo`, `GetUserPwInfo`), and `libnet_SetPassword()` with `LIBNET_SET_PASSWORD_SAMR_HANDLE`. `libnet_JoinADSDomain()` uses DRSUAPI `DsBind`/`DsCrackNames` and LDAP writes through LDB. `libnet_Join_member()` wraps `JoinDomain` for workstation trust accounts and calls `provision_store_self_join()`.

## Control Flow
`libnet_JoinDomain()` connects to a SAMR pipe either automatically by domain or through a specified binding. It ensures domain name and SID are known, opens the domain, and attempts `samr_CreateUser2` for the requested account name/type. If the user exists, it looks up and opens the user; when `recreate_account` is true, it deletes and recreates the account. It then queries account flags, verifies that existing trust type matches the requested account type, clears disabled/password-not-required bits, gets password policy, chooses caller-provided or generated password, and calls `libnet_SetPassword()` with `samr_UserInfo21` to set full name and account flags.

After SAMR success, the function fills output fields: join password, domain SID/name/realm, account SID, SAMR pipe/binding, user handle, error string, KVNO default, and server DN default. If a realm exists, `libnet_JoinADSDomain()` completes AD-specific steps. That helper switches the SAMR binding to sealed DRSUAPI over TCP when appropriate, binds, cracks the account SID to a DN, opens LDAP to the target host, reads the account's `msDS-KeyVersionNumber`, SPNs, DNS hostname, and GUID, writes `servicePrincipalName` and `dNSHostName`, attempts to set `msDS-SupportedEncryptionTypes`, cracks the domain name to a DN, stores account/domain DN/KVNO/GUID outputs, and invokes `libnet_JoinSite()` for server-trust joins.

`libnet_Join_member()` chooses or derives the local NetBIOS name, appends `$` for the account, calls `libnet_JoinDomain()` as `ACB_WSTRUST`, builds `provision_store_self_join_settings`, stores local join secrets via provisioning code, and moves selected outputs back to the caller.

## State And Persistence Behavior
Remote persistent effects include machine account creation/deletion/recreation, password reset, account-flag update, SPN and DNS hostname LDAP replacement, encryption-type update when supported, and possible site/server updates for DC joins through `libnet_JoinSite()`. Local persistent effects happen only in `libnet_Join_member()`, which writes self-join secrets including domain, realm, NetBIOS name, secure channel type, machine password, KVNO, and domain SID.

The function also returns live SAMR pipe/user handles by reparenting them to the caller context. Generated passwords are returned in output and then used for local secret storage by the member wrapper.

## Dependencies And Integration Points
Dependencies include SAMR and DRSUAPI generated RPC clients, `libnet_RpcConnect`, `libnet_SetPassword`, LDAP/LDB wrappers, samdb helpers, Kerberos encryption constants, credentials, loadparm, and provisioning secret-storage APIs. `libnet_join.h` defines the request/result structures. Site integration is delegated to `libnet_JoinSite()`.

## Risks
The join path has many partial-mutation points: account creation or deletion can succeed before password/SPN/site steps fail. `recreate_account` is destructive. Existing account type mismatches are rejected, but newly created accounts with unexpected type also fail after creation. ADS finishing assumes DRSUAPI `DsCrackNames` and LDAP writes are available; older or non-AD domains skip this only if no realm was discovered. SPN replacement writes only HOST SPNs built from NetBIOS and realm, which can overwrite pre-existing servicePrincipalName values through `dsdb_replace`. Error strings vary between detailed messages and null on allocation failures.

## Test Signals
Tests should cover automatic and specified-binding joins, new account creation, existing account reuse, account-type mismatch, destructive recreate, password-policy minimum length, caller-provided password, generated password, AD finishing with KVNO/account DN/domain DN outputs, encryption-type write tolerated on old schema, member join secret persistence, and failure cleanup expectations. Integration coverage requires a test DC because the code depends on real SAMR/DRSUAPI/LDAP semantics.
