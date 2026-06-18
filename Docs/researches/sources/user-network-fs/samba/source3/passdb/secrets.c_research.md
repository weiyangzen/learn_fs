# sources/user-network-fs/samba/source3/passdb/secrets.c

## Purpose
`secrets.c` implements source3 accessors for Samba's private `secrets.tdb` database. This database stores generated/private local state such as machine and domain trust material, LDAP bind passwords, AFS keys, fallback IPC credentials, generic owner/key secrets, and other sensitive blobs used by passdb and authentication code.

## Important APIs, types, and functions
- `secrets_init_path(private_dir)`, `secrets_init()`, `secrets_db_ctx()`, and `secrets_shutdown()` manage the singleton `struct db_context *db_ctx` for `secrets.tdb`.
- `secrets_fetch`, `secrets_store`, `secrets_delete_entry`, and `secrets_delete` are generic key/value helpers over dbwrap/TDB.
- `secrets_store_creds` stores module-level IPC auth username/domain/password records from `cli_credentials`.
- `secrets_fetch_trusted_domain_password`, `secrets_store_trusted_domain_password`, and `trusted_domain_password_delete` marshal `TRUSTED_DOM_PASS` NDR blobs under uppercased domain-trust keys.
- `secrets_store_ldap_pw` and `fetch_ldap_pw` manage LDAP admin bind passwords.
- `secrets_store_afs_keyfile` and `secrets_fetch_afs_key` store and retrieve AFS keyfile data.
- `secrets_fetch_ipc_userpass`, `secrets_store_generic`, and `secrets_fetch_generic` handle fallback IPC credentials and namespaced generic secrets.

## Control flow
All public operations first ensure the database is opened, normally at `lp_private_dir()/secrets.tdb` or an explicit path supplied by `secrets_init_path`. Fetching reads a TDB record into a temporary dbwrap buffer, duplicates it with `smb_memdup`, burns and frees the dbwrap buffer, and returns a malloc-style pointer for the caller to free. Storing uses `dbwrap_trans_store` with `TDB_REPLACE`; deletion uses transactional delete after an existence check for the idempotent `secrets_delete`.

Typed helpers build stable key strings and serialize/deserialize domain-specific records. Trusted-domain passwords are encoded with generated NDR push/pull functions and include domain name, modification time, plaintext trust password, and domain SID. LDAP and generic secrets use string keys and null-terminated string values. AFS retrieval validates exact structure size and key count before returning the highest-index key after network-to-host conversion.

## State and persistence behavior
Persistent state is the on-disk `secrets.tdb`, opened mode `0600` with `O_RDWR|O_CREAT`. The `db_ctx` singleton remains live until `secrets_shutdown`; once initialized, later `secrets_init_path` calls return true without reopening to a new path. Sensitive fetched buffers are explicitly burned where this file knows their size, and some returned talloc data is marked with `talloc_keep_secret` after NDR unmarshalling.

## Dependencies and integration points
The file depends on dbwrap/tdb, loadparm private-dir configuration, generated `ndr_secrets`, `libcli_auth`, credentials APIs, SID/security helpers, and Samba memory-scrubbing utilities. It underpins `secrets_lsa.c`, `py_passdb.c`, machine trust and domain trust management, LDAP passdb support, and code needing fallback IPC credentials.

## Risks and edge cases
- The singleton database path is sticky after first initialization; tests that switch private directories must control process state or call shutdown before reopening.
- Callers own returned buffers and must free/burn them correctly. Missing scrubbing outside this file can leak secret material.
- `secrets_fetch_trusted_domain_password` returns duplicated plaintext password and optional SID/time; partial allocation failure can leave callers without all requested fields.
- AFS key retrieval assumes at least one key after validating only max count; malformed zero-key keyfiles would index `entry[i-1]`.
- Key construction for generic and LDAP secrets uses raw owner/key/DN strings, so callers must avoid collisions or unexpected separators.

## Test signals
Tests should use a temporary private directory with a fresh `secrets.tdb`, verify generic store/fetch/delete and idempotent delete, round-trip trusted-domain password NDR data including SID and modification time, reject malformed LDAP password records without null termination, and validate secrets are not reopened to a different path after the singleton is initialized.
