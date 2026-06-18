# sources/user-network-fs/samba/source3/torture/pdbtest.c

## Purpose
`pdbtest.c` is a standalone passdb backend validation utility. It creates a synthetic Samba account, verifies fields round-trip through a selected passdb backend, checks NTLM authentication/session-key behavior, and optionally tests trusted-domain persistence.

## Important APIs, types, and functions
`samu_correct()` compares many `struct samu` fields: usernames, account control, password hashes, password history, logon times, profile/home/script paths, logon hours, and SIDs. `test_auth()` builds NTLM challenge/response data and compares session keys from `check_sam_security_info3`, auth3, and winbind when available. `test_trusted_domains()` exercises `set_trusted_domain`, `get_trusted_domain`, and `del_trusted_domain`.

## Control flow
`main()` initializes Samba command-line/config handling, chooses `--backend` or `lp_passdb_backend()`, gets a Unix user (default `nobody`), builds a `samu`, fills account/profile/password/time fields, adds it through the backend, reads it back, validates it, authenticates it, deletes it, and then tests trusted domains if the backend advertises `PDB_CAP_TRUSTED_DOMAINS_EX`.

## State and persistence behavior
The utility writes a real passdb account and deletes it before exit. It may also write and delete a trusted-domain entry named `trustdom`. Random password/hash/history data is generated per run. Failures during add/read/delete can leave backend state behind.

## Dependencies and integration points
It integrates with passdb modules, Samba account-policy APIs, auth subsystem helpers, generated NDR DRS trust blobs, dom_sid utilities, tsocket, and wbclient. `wscript_build` builds it as the standalone `pdbtest` binary.

## Risks and test signals
Because it mutates the configured passdb backend, it must be run only against test backends. A pass indicates both persistence and authentication interoperability for common fields. It explicitly tolerates missing winbind (`WBC_ERR_WINBIND_NOT_AVAILABLE`) but treats other winbind/auth mismatches as failures.
