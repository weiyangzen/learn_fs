# sources/user-network-fs/samba/source3/include/secrets.h

## Purpose
`secrets.h` defines key names, data formats, and APIs for Samba's private secrets database. It covers machine account passwords, previous passwords, domain SID/GUID, LDAP bind passwords, schannel keys, authenticated IPC credentials, AFS keyfiles, generic secrets, Kerberos salting principals, machine password changes, trusted domain passwords, and LSA secrets.

## Important APIs, Types, And Control Flow
String constants define stable keys under `SECRETS/` and related namespaces. `struct machine_acct_pass` stores an NT hash and modification time. `struct afs_key` and `struct afs_keyfile` model OpenAFS keyfiles with up to eight keys. APIs initialize/shutdown the secrets DB, fetch/store/delete raw entries, store credentials, manage domain protection/SID/GUID, fetch/store trusted domain and machine passwords, handle join context storage, debug and stringify domain info, prepare/fail/defer/finish password changes, delete machine/domain secrets, manage LDAP passwords, AFS keys, IPC credentials, generic owner/key secrets, Kerberos DES salt, and get/set/delete LSA secrets with old/current blobs and security descriptors.

## State And Persistence
The primary persistent state is `secrets.tdb` under Samba's private directory, initialized by `secrets_init_path()` or `secrets_init()`. Password change APIs preserve current and previous password material, last-change times, secure channel type, supported encryption data, and salting principal information. LSA secret APIs track current and old values plus timestamps and security descriptors.

## Dependencies And Integration Points
It depends on replace, generated security types, DATA_BLOB, GUID/SID/NTTIME/NTSTATUS, netlogon secure channel enums, CLI credentials, libnet join context, and secrets domain info structures. It integrates with domain join, Netlogon trust password changes, winbind, LDAP auth, Kerberos keytab sync callbacks, passdb secret wrappers, and LSA RPC secret management.

## Risks And Test Signals
Risks include plaintext secret exposure, incorrect previous-password handling during failed/deferred changes, domain/realm deletion mismatch, stale keytab sync after password changes, insecure generic secret ownership, and security descriptor loss for LSA secrets. Test signals include secrets DB init/fetch/store/delete, machine password rotation success/fail/defer flows, previous password retrieval, trusted domain password CRUD, domain SID/GUID persistence, LDAP password storage, AFS key lookup, IPC credential fetch, generic secret round trips, Kerberos salt storage, and LSA secret old/current timestamp/security descriptor tests.
