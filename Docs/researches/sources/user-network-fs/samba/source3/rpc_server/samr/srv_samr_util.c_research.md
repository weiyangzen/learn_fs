# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.c

## Purpose

`srv_samr_util.c` implements SAMR utility routines that copy SAMR user information structures into Samba passdb `struct samu` records. It is the normalization layer behind many `_samr_SetUserInfo()` levels in `srv_samr_nt.c`: narrow info levels are converted into a synthetic `samr_UserInfo21` with the right `fields_present` mask, then `copy_id21_to_sam_passwd()` applies only the requested fields.

## Important APIs, Types, and Functions

- `copy_id2_to_sam_passwd()` through `copy_id18_to_sam_passwd()`: wrap smaller SAMR info levels and delegate to `copy_id21_to_sam_passwd()`.
- `copy_id20_to_sam_passwd()`: handles user parameters separately by base64-encoding the binary parameter blob into passdb `munged_dial`.
- `copy_id21_to_sam_passwd()`: central field copier for `samr_UserInfo21`. It updates timestamps, strings, primary group, account flags, logon hours, counters, expiration behavior, country code, and code page.
- `copy_id23_to_sam_passwd()`, `copy_id25_to_sam_passwd()`, `copy_id32_to_sam_passwd()`: delegate nested `info` members to level 21 copying.
- `copy_id24_to_sam_passwd()` and `copy_pwd_expired_to_sam_passwd()`: update password-expired behavior through the level-21 expired flag path.
- `STRING_CHANGED` and `STRING_CHANGED_NC`: local macros used to avoid marking unchanged strings as modified; the `_NC` form tolerates NULL transitions.

## Control Flow

Most wrappers allocate a stack `samr_UserInfo21`, zero it, set `fields_present` and the few fields represented by their SAMR level, then call `copy_id21_to_sam_passwd()` with a log prefix. This keeps passdb mutation semantics centralized and avoids divergent handling of identical fields across info levels.

`copy_id21_to_sam_passwd()` checks each `SAMR_FIELD_*` bit before reading a field. For time fields it converts NT time to Unix time and updates passdb only if the stored value differs. For string fields it requires a non-NULL SAMR string pointer and compares against current passdb values before calling `pdb_set_*()` with `PDB_CHANGED`. For binary parameters it base64-encodes the SAMR binary string and stores it as `munged_dial`.

Primary RID changes are deliberately not applied; the function logs attempts to change user RID. Primary group RID changes are applied through `pdb_set_group_sid_from_rid()`. Account flag updates include special handling for `ACB_AUTOLOCK`: clients cannot newly set autolock through set-info, and clearing autolock resets bad-password counters and time. Password-expired changes set `pass_last_set_time` to zero for must-change only when password changes are allowed; clearing the flag may set the last-set time to `now` only when the existing password is considered expired.

Logon hours are copied as divisions, byte length, and bit array after comparing hex-rendered hour strings. Bad-password count and logon count are copied when present. Country code and code page are copied when present.

## State and Persistence Behavior

The functions mutate an in-memory `struct samu`; they do not write to passdb themselves except indirectly through passdb setter flags. Callers are responsible for later persistence with `pdb_update_sam_account()` and related group-update operations. Each setter uses `PDB_CHANGED` for actual changes, so passdb backends can decide which attributes to persist.

The only data transformation with a storage format is SAMR user parameters: binary `lsa_BinaryString` data is stored in passdb as base64 text in `munged_dial`, and empty blobs map to NULL/empty encoded state depending on caller input.

## Dependencies and Integration Points

The file depends on generated SAMR structures, passdb getter/setter APIs, base64 helpers, NT-time conversion helpers, account policy reads for password-expiration decisions, and Samba debug logging. It is directly included by `srv_samr_nt.c` through `srv_samr_util.h` for all user-info update paths.

## Risks and Edge Cases

- Fields are only applied if `fields_present` is set, and many string fields additionally require a non-NULL `.string`. A caller expecting NULL to clear a field will not get that behavior for most string fields.
- `copy_id21_to_sam_passwd()` mutates `from->acct_flags` by clearing `ACB_AUTOLOCK` in one branch, so callers should not treat the input structure as immutable afterward.
- Password-expired clearing uses current time and account policy to decide whether to update `pass_last_set_time`; subtle policy changes can affect wire-visible behavior.
- User RID changes are ignored by design, while primary group RID changes have real system consequences once callers persist and sync UNIX primary groups.
- Base64 parameter conversion asserts allocation success after `base64_encode_data_blob()`, which is consistent with local style but can abort in severe memory failure.

## Test Signals

Focused tests should verify each wrapper sets the expected `fields_present` subset, `copy_id21_to_sam_passwd()` persists only marked fields, unchanged strings do not mark passdb fields dirty, NULL strings are not treated as clears, primary RID changes are ignored, primary group RID changes are marked, autolock cannot be newly set but clearing it resets bad-password state, expired-flag behavior matches password policy, logon hours copy correctly, and binary parameters round trip through base64 storage.
