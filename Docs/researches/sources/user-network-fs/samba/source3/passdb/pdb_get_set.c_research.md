# sources/user-network-fs/samba/source3/passdb/pdb_get_set.c

## Purpose

`pdb_get_set.c` is the field access layer for `struct samu`. It centralizes getters, setters, calculated password times, change/set/default bitmaps, SID/group handling, password hash storage, plaintext password handling, password history rotation, and backend private data attachment.

## Important APIs And Functions

Password time helpers are `pdb_is_password_change_time_max()`, private `pdb_password_change_time_max()`, `pdb_get_pass_can_change_time()`, `pdb_get_pass_can_change_time_noncalc()`, `pdb_get_pass_must_change_time()`, and `pdb_get_pass_can_change()`. Getter/setter APIs cover account control, times, logon hours, hashes, password history, plaintext password, SIDs, strings, counters, locale fields, `unknown_6`, and backend private data. Higher-level helpers include `pdb_set_init_flags()`, `pdb_set_pass_can_change()`, `pdb_set_plaintext_passwd()`, `pdb_update_history()`, `pdb_build_fields_present()`, `pdb_element_is_changed()`, and `pdb_element_is_set_or_changed()`.

## Control Flow And State

Getters generally expose stored fields directly, but password change times are calculated from account policy. A last-set time of zero disables or short-circuits change calculations. `ACB_PWNOEXP` forces a stable maximum password-must-change value. `pdb_set_init_flags()` lazily allocates two bitmaps; `PDB_CHANGED` sets both, `PDB_SET` clears changed and sets set, and `PDB_DEFAULT` clears both.

User SIDs are copied directly. Group SID setting allocates a cached SID and accepts the supplied SID only if it is Domain Users or maps to a gid; otherwise it falls back to Domain Users. `pdb_get_group_sid()` lazily computes the primary group SID from Unix primary gid when no explicit group SID is cached. Password setting stores NT and LM hashes in `DATA_BLOB`s, drops changed LM hashes when LANMAN auth is disabled or the password is too long, stores plaintext for backends that need it, updates `pass_last_set_time`, and rotates password history.

## Persistence Behavior

This file does not directly persist to disk. It prepares in-memory `struct samu` state and changed/default flags that backend update routines interpret. Sensitive blobs are cleared before replacement; plaintext is burned before overwrite. Password-history size follows `PDB_POLICY_PASSWORD_HISTORY`.

## Dependencies And Integration Points

Dependencies include `passdb.h`, auth hash helpers, SID/security helpers, and bitmap utilities. The functions are used heavily by `passdb.c` serialization, backend implementations, RPC account management, authentication, and local password change flows.

## Risks And Test Signals

Calculated password dates can differ from raw stored dates, so serialization and backend loading must use the non-calculated getter where appropriate. String setters use `PDB_NOT_QUITE_NULL` because older callers expect non-null strings. Group SID fallback can hide an unmapped group SID by replacing it with Domain Users. `pdb_update_history()` copies current history into a buffer sized by current policy, making policy shrinkage a risk area. Tests should cover password date policies, max-time compatibility, flag transitions, null string compatibility, SID/group fallback, LANMAN enabled/disabled hash behavior, plaintext burn/replace, history rotation with policy changes, backend-private destructor invocation, and changed/set checks.
