# sources/user-network-fs/samba/source3/librpc/crypto/gse_krb5.c

## Purpose
`gse_krb5.c` provides Kerberos keytab helpers for GSE server-side authentication. Its central job is to create a unique in-memory keytab containing keys from Samba secrets, the system keytab, a dedicated keytab, or combinations selected by `kerberos method`.

## Important APIs, types, and functions
- `gse_krb5_get_server_keytab()` is the exported entry point. It resolves a unique `MEMORY:cifs_srv_keytab-<krbctx>` keytab and populates it according to configuration.
- `fill_mem_keytab_from_secrets()` reads the machine account secrets database and writes current, old, older, and next-change keys into the memory keytab.
- `fill_mem_keytab_from_system_keytab()` copies only acceptable host/cifs/machine-account principals from the system keytab.
- `fill_mem_keytab_from_dedicated_keytab()` copies all entries from `lp_dedicated_keytab_file()`.
- `fill_keytab_from_password()` filters secrets-derived Kerberos keys by allowed enctypes and writes keytab entries.
- `flush_keytab()` removes all entries from a keytab, restarting iteration after each mutation.

## Control flow
`gse_krb5_get_server_keytab()` creates a fresh memory keytab, then switches on `lp_kerberos_method()`. Secrets mode loads and possibly upgrades secrets, derives the realm and machine principal, checks whether the memory keytab has a private cleartext marker, flushes stale entries, and writes acceptable keys. System-keytab mode builds an allowlist of expected machine, host, and cifs principals and copies matching entries. Dedicated-keytab mode copies all entries from the configured file. Combined mode tries secrets and system keytab, succeeding if either source populated the memory keytab.

## State and persistence behavior
The produced keytab is in-memory and owned by the caller's Kerberos context. The code reads persistent state from Samba secrets and optional keytab files but does not modify those persistent stores. It writes a private keytab entry with enctype `-99` containing the cleartext machine password so later calls can detect whether the generated memory keytab is already current. Secrets structures include current, old, older, and staged next-change passwords, letting acceptor credentials survive password rollovers.

## Dependencies and integration points
The helper depends on Kerberos APIs, Samba `smb_krb5` wrappers, loadparm, secrets storage, generated NDR secrets structs, and constant-time comparison utilities. `gse.c` calls it during server GENSEC startup before importing acceptor credentials with `smb_gss_mech_import_cred()`.

## Risks and edge cases
The file handles secret material directly. Risks include leaking cleartext markers, accepting the wrong keytab principal, failing rollover when kvno values are placeholder-derived, and platform differences in keytab cursor behavior. Filtering system keytab entries depends on exact string forms and case-insensitive comparison, so hostname/realm canonicalization changes can affect authentication. Error cleanup must close cursors and keytabs even on partially-read entries.

## Test signals
Tests should cover all `kerberos method` modes, missing/invalid secrets, dedicated keytab open failure, system keytab principal filtering, password rollover with old/older/next-change keys, unsupported enctype filtering, repeated calls with unchanged secrets, and failure cleanup under keytab iteration errors.
