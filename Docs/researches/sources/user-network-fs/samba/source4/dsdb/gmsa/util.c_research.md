# sources/user-network-fs/samba/source4/dsdb/gmsa/util.c

## Purpose

`gmsa/util.c` implements Group Managed Service Account password access, derivation, packing, recalculation, and database update support. It computes gMSA passwords from GKDI root keys and account SID, determines when managed password IDs are stale, builds system password-update requests, updates `msDS-ManagedPasswordId`/previous ID, supports operational `msDS-ManagedPassword` blob generation, and redacts secrets on RODCs.

## Important APIs, Types, and Functions

- `gmsa_allowed_to_view_managed_password()` enforces `msDS-GroupMSAMembership` security descriptor access checks, allowing system unconditionally.
- `struct RootKey` models no key, a specific `KeyEnvelopeId`, a nonspecific key-start-time lookup, or an obtained root key plus derived password.
- `gmsa_managed_pwd_id()`, `gmsa_update_managed_pwd_id()`, and `gmsa_pack_managed_pwd_id()` parse/create/update/pack GKDI `KeyEnvelope` password IDs.
- `gmsa_specific_password()`, `gmsa_nonspecific_password()`, `gmsa_fetch_root_key()`, and `gmsa_get_root_key()` retrieve root keys and derive passwords.
- `gmsa_system_update_password_id_req()` builds an LDB modify request for current and previous password ID attributes and marks it `DSDB_FLAG_AS_SYSTEM`.
- `gmsa_generate_blobs()` creates a fresh managed password ID blob and password from the most recent root key usable within one GKDI interval.
- `gmsa_create_update()` prepares old password, new password, and password-ID update requests.
- `gmsa_pack_managed_pwd()` packs a `MANAGEDPASSWORD_BLOB` for operational attribute reads.
- `dsdb_account_is_gmsa()`, `gmsa_get_managed_pwd_id()`, `samdb_gmsa_key_is_recent()`, and `gmsa_recalculate_managed_pwd()` implement account classification and rollover logic.
- `dsdb_update_gmsa_entry_keys()` applies a prepared update transactionally after verifying the managed password ID has not changed.
- `dsdb_update_gmsa_keys()` updates all gMSA entries in a search result or redacts secrets when running on an RODC.
- `dsdb_gmsa_current_time()` and `dsdb_gmsa_set_current_time()` support real or test-injected time via LDB opaque `DSDB_GMSA_TIME_OPAQUE`.

## Control Flow

Access checks first inspect DSDB session info. System users are allowed; normal users must have read-property access through the `msDS-GroupMSAMembership` security descriptor using the account SID as object context.

Password derivation starts from a specific password ID or a desired key start time. Specific lookups fetch the root key by GUID and use the GKID from the ID. Nonspecific lookups select the most recently created root key with `UseStartTime <= key_start_time` and derive the GKID for that interval. `gmsa_fetch_root_key()` converts these pending descriptions into obtained root keys and derived null-terminated passwords; missing nonspecific keys are tolerated as "no key" for cases like optional previous passwords.

`gmsa_recalculate_managed_pwd()` is the main policy engine. It reads the rollover interval, creation time, object SID, and current `msDS-ManagedPasswordId`. If the current key has not expired, no database update is needed, although requested operational return data may still be derived. If expired or absent, it calculates the next key start time, determines whether the current key becomes the previous key, derives current and optional previous passwords, and creates update requests. For operational reads near expiration, it may return a future key as current and the existing current key as previous, extending `unchanged_interval` accordingly.

`dsdb_update_gmsa_entry_keys()` wraps updates in one transaction. Before applying requests, it re-reads `msDS-ManagedPasswordId` and compares it with the value observed during planning. If it differs, the function returns success without writing so the caller can retry the search. It then performs optional old password update, current password update, and password-ID update in order.

## State and Persistence Behavior

Persistent attributes touched include `unicodePwd`/password hashes through `gmsa_system_password_update_request()`, `msDS-ManagedPasswordId`, and `msDS-ManagedPasswordPreviousId`. The operational `msDS-ManagedPassword` blob is packed for return but not persisted by `gmsa_pack_managed_pwd()`. `dsdb_update_gmsa_keys()` only writes when connected locally through the partition module opaque; non-local connections skip writes. RODCs remove secret attributes from result messages so clients can be referred to writable DCs.

## Dependencies and Integration Points

The file integrates with GKDI storage APIs, `lib/crypto/gmsa`, generated GKDI/GMSA/security NDR, DSDB password update helpers, LDB requests/transactions, security descriptor access checks, session info opaques, and samdb RODC detection. It is used by DSDB search/operational attribute paths and KDC-facing account lookup flows.

## Risks

This code is secret-handling and time-sensitive. A wrong rollover calculation can make gMSA passwords stale, future-dated, or unavailable until time catches up. The comments explicitly note that out-of-band password resets are not detected until rollover because the managed password ID is treated as the source of truth. Missing root keys can make a gMSA unusable until the next rollover or permanently if required root keys are deleted. Transactional verification prevents overwriting concurrent updates but requires callers to honor `retry_out`. RODC redaction must remain complete for all secret attributes.

## Test Signals

Tests should cover system and non-system access checks, malformed membership security descriptors, absent/invalid password IDs, current-key-valid no-op, expired-key update creation, account younger than rollover, previous password ID handling, future-key return within max clock skew, missing specific root key error, missing nonspecific previous key tolerance, transaction conflict no-op, update request ordering, RODC secret redaction, non-local no-write behavior, test time opaque behavior, and NDR packing for `KeyEnvelope` and `MANAGEDPASSWORD_BLOB`.
