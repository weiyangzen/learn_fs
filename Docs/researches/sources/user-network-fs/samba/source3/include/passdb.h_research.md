# sources/user-network-fs/samba/source3/include/passdb.h

## Purpose
`passdb.h` is the central source3 account database interface. It defines SAM account records, group mapping records, search state, domain/trust structures, account policy identifiers, password history constants, backend capability bits, and the versioned `pdb_methods` module ABI used by passdb backends.

## Important APIs, Types, And Control Flow
Important types include `GROUP_MAP`, `acct_info`, `login_cache`, `struct samu`, `samr_displayentry`, `pdb_search`, `pdb_domain_info`, `pdb_trusted_domain`, `trustdom_info`, `enum pdb_policy_type`, and `struct pdb_methods`. `struct samu` tracks account fields, SIDs, password hashes/history/plaintext password, logon times, account flags, hours, counters, private backend data, and initialization/change bitmaps. `pdb_methods` is the backend vtable for user CRUD, group and alias management, SID/name lookup, account policies, searches, idmap, RID generation, trusted domains, secrets, UPN suffixes, responsibility routing, and backend cleanup. Public wrappers initialize and dispatch to the selected backend, manipulate `samu` fields, encode/decode password fields, update lockout counters, manage account policy/login cache, and access secrets-backed domain SID/GUID data.

## State And Persistence
Passdb state is persistent in selected backends such as tdbsam, LDAP, or secrets-backed storage. The header also defines transient `samu` objects with change tracking, search caches, login cache entries, trusted-domain blobs, account policy values, RID allocation state, and backend private data with custom destructors.

## Dependencies And Integration Points
It depends on generated LSA types, tevent, talloc, domain SIDs/GUIDs, DATA_BLOB, NTSTATUS, security descriptors, CLI credentials, unix id mapping, machine SID and lookup SID helpers, and passdb modules. It integrates with SAMR/LSA RPC servers, authentication, winbind/idmap, local user/group management, domain join/trust handling, account lockout, password change policy, and secrets storage.

## Risks And Test Signals
Risks include backend ABI version mismatch (`PASSDB_INTERFACE_VERSION`), incomplete change/set flag handling, password hash/history mishandling, RID algorithm collisions, search cache lifetime bugs, trust secret exposure, inconsistent responsibility routing between backends, and replicated SAM lockout cache errors. Test signals include backend registration/version tests, create/update/delete/rename user flows, group/alias membership enumeration, SID/name lookup, account policy defaults and persistence, bad password lockout transitions, password history update, trusted domain CRUD, UPN suffix CRUD, idmap round trips, `samu` serialization buffer versions, and secret get/set/delete through passdb.
