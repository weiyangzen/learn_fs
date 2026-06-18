# sources/user-network-fs/samba/source3/passdb/passdb.c

## Purpose

`passdb.c` contains core `struct samu` lifecycle, Unix-account initialization, account-control and password/hour hex helpers, algorithmic RID mapping, local password changes, legacy TDB buffer serialization, bad-password policy updates, and trust credential fetch helpers. It is central glue between Unix passwd/group state, Samba account records, local SAM SID logic, secrets storage, and credentials construction.

## Important APIs And Functions

Lifecycle and Unix initialization are handled by `samu_new()`, `samu_set_unix()`, `samu_alloc_rid_unix()`, and private `samu_set_unix_internal()`. Utility APIs include `pdb_encode_acct_ctrl()`, `pdb_decode_acct_ctrl()`, `pdb_sethexpwd()`, `pdb_gethexpwd()`, `pdb_sethexhours()`, `pdb_gethexhours()`, algorithmic RID conversion functions, `lookup_global_sam_name()`, and `local_password_change()`. Serialization APIs are `init_samu_from_buffer()`, `init_buffer_from_samu()`, and `pdb_copy_sam_account()`. Policy/trust helpers include `pdb_update_bad_password_count()`, `pdb_update_autolock_flag()`, `pdb_increment_bad_password_count()`, `get_trust_pw_clear()`, `get_trust_pw_hash()`, and `pdb_get_trust_credentials()`.

## Control Flow And State

`samu_new()` allocates a zeroed account, attaches `samu_destroy()` to wipe password blobs/plaintext, sets NT-compatible default times, logon hours, counters, string fields, and normal-user account control. `samu_set_unix_internal()` populates a `samu` from `struct passwd`, trims chfn-style GECOS fields, sets default profile/home/drive/script substitutions, marks workstation accounts ending in `$`, handles guest RID 501, and either asks a backend for a new RID or derives one algorithmically from uid.

`local_password_change()` reads the target account, handles delete early, optionally creates a user/trust/interdomain account, updates flags for no-password/disable/enable, hashes a new plaintext password through `pdb_set_plaintext_passwd()`, and commits with `pdb_update_sam_account()`. Serialization readers unpack V0-V4 TDB formats, reconstruct defaults when fields are absent, handle password history and comments, and convert 32-bit stored times; writers emit the latest V4/V3 layout and store only non-default path fields.

Bad-password functions enforce reset and lockout policies by clearing expired state, incrementing counters, and setting `ACB_AUTOLOCK` at threshold. Trust helpers distinguish DC trusted-domain cases from member/self-joined cases, read current and previous machine passwords from secrets, fall back to legacy hash secrets, and build `cli_credentials` with Kerberos enabled or disabled according to domain type and available secret material.

## Persistence Behavior

`struct samu` state is transient until passdb backend calls persist it. Serialization functions define the binary representation used by TDB-style passdb backends. Local password changes persist through backend methods. Trust credentials read persistent secrets and trusted-domain passdb records. Account policies are read from passdb policy storage and influence computed times, history length, lockout behavior, and serialization.

## Dependencies And Integration Points

This file depends on `passdb.h`, Unix passwd/group APIs, loadparm, auth credentials, secrets, security SID helpers, substitution helpers, and tdb pack/unpack utilities. It calls setter/getter APIs from `pdb_get_set.c`, global SID APIs from `machine_sid.c`, backend dispatchers from `pdb_interface.c`, and secrets functions from `machine_account_secrets.c`.

## Risks And Test Signals

Legacy serialization is compatibility-sensitive, especially 32-bit time conversion, absent default path fields, and password history sizing under policy changes. `pdb_gethexhours()` appears to call `hex_byte(p, ...)` inside a loop without advancing `p + i`, which is a notable defect signal. Tests should cover `samu_new()` defaults, Unix conversion for guest/user/workstation accounts, RID round-trips, account-control encode/decode, local password flows, all serialized versions, password history truncation/rotation, bad-password/autolock policies, trust credential fallback branches, hash-only fallback, and root delete/rename protections.
