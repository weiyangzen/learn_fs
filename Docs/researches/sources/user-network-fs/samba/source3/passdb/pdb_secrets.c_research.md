# sources/user-network-fs/samba/source3/passdb/pdb_secrets.c

## Purpose
`pdb_secrets.c` provides passdb-facing helpers around Samba's secrets database. Its main job is to enumerate trusted domains stored in `secrets.tdb` and expose a small set of wrapper functions so passdb modules can store/fetch domain SID and GUID data without directly linking against the lower-level secrets library.

## Important APIs, Types, And Functions
`struct list_trusted_domains_state` accumulates `struct trustdom_info` pointers and a count while traversing the secrets database. `list_trusted_domain()` is the dbwrap traversal callback: it filters keys with the `SECRETS_DOMTRUST_ACCT_PASS` prefix, parses values as NDR `TRUSTED_DOM_PASS`, validates domain SID shape, and appends a `trustdom_info` containing the trusted domain name and SID.

`secrets_trusted_domains()` initializes secrets, fetches the secrets db context, allocates the result array under the caller's talloc context, traverses the database, and returns the accumulated array and count. The `PDB_secrets_*` wrappers call the corresponding secrets functions for domain SID/GUID storage and protection flags: `PDB_secrets_store_domain_sid()`, `PDB_secrets_mark_domain_protected()`, `PDB_secrets_clear_domain_protection()`, `PDB_secrets_fetch_domain_sid()`, `PDB_secrets_store_domain_guid()`, and `PDB_secrets_fetch_domain_guid()`.

## Control Flow
Trusted-domain enumeration starts with `secrets_init()`. If secrets cannot be initialized, enumeration returns `NT_STATUS_ACCESS_DENIED`. The traversal callback ignores unrelated keys, attempts to NDR-decode trust password records, rejects decoded SIDs that do not look like account-domain SIDs, allocates `trustdom_info`, copies the Unicode trust name and SID, and expands the caller-owned array with `ADD_TO_ARRAY`.

Wrapper functions are simple pass-throughs and preserve the boolean semantics of the underlying secrets API.

## State And Persistence
Persistent state is in `secrets.tdb`, accessed through `secrets_db_ctx()` and dbwrap. This file does not define its own schema; it relies on `SECRETS_DOMTRUST_ACCT_PASS` key prefixes and generated NDR for `TRUSTED_DOM_PASS`. Enumerated results are transient talloc allocations owned by the caller.

The domain SID/GUID wrappers mutate or read secrets records and protection marks, which are later used by passdb backends such as `pdb_samba_dsdb.c` to keep source3-visible domain identity synchronized with DSDB.

## Dependencies And Integration Points
The file depends on passdb types, generated NDR for secrets records, `secrets.h`, dbwrap traversal APIs, security SID utilities, and TDB utility helpers. It is an integration shim between passdb modules and the secrets subsystem, especially for trusted-domain enumeration and local-domain identity storage.

## Risks
`list_trusted_domain()` returns `false` on NDR parse failure even though traversal callbacks conventionally use integer status; this is numerically zero and therefore continues traversal rather than stopping. That is likely intentional tolerance for bad records, but it can hide malformed trust entries. The callback validates only `num_auths == 4`, not all domain SID invariants. Allocation failure after `ADD_TO_ARRAY` is handled by resetting count and returning `-1`, but `secrets_trusted_domains()` does not inspect the traverse return in this file, so partial or failed enumeration can still return `NT_STATUS_OK`.

## Test Signals
Tests should create secrets records with valid and invalid `SECRETS_DOMTRUST_ACCT_PASS` values, unrelated keys, malformed NDR blobs, non-domain SIDs, and allocation-failure injection where possible. Wrapper tests should verify SID/GUID store/fetch and protection flag behavior through the public `PDB_secrets_*` functions rather than directly through secrets internals.
