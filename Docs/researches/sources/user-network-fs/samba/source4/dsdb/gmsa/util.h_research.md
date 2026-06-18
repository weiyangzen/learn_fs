# sources/user-network-fs/samba/source4/dsdb/gmsa/util.h

## Purpose

`gmsa/util.h` declares the public DSDB gMSA utility contract for managed password access checks, password ID packing, password derivation, operational password blob packing, account classification, managed password recalculation, database updates, and testable current time.

## Important APIs, Types, and Functions

- `struct gmsa_update` carries a prepared update: target DN, originally observed password ID, optional previous-password request, current-password request, and password-ID modify request.
- `struct gmsa_update_pwd_part` pairs a `ProvRootKey` with a `Gkid`.
- `struct gmsa_update_pwd` groups previous and new password parts.
- `gmsa_allowed_to_view_managed_password()` checks whether a caller can read a gMSA managed password.
- `gmsa_update_managed_pwd_id()` and `gmsa_pack_managed_pwd_id()` mutate and encode `KeyEnvelope` password IDs.
- `gmsa_generate_blobs()` produces a managed password ID blob and derived password for account creation or initialization.
- `gmsa_pack_managed_pwd()` encodes the operational `MANAGEDPASSWORD_BLOB`.
- `dsdb_account_is_gmsa()` identifies gMSA objects by objectClass.
- `gmsa_get_managed_pwd_id()` extracts a `KeyEnvelopeId`.
- `struct gmsa_return_pwd` carries previous/current passwords and query/unchanged intervals for operational reads.
- `samdb_gmsa_key_is_recent()`, `gmsa_recalculate_managed_pwd()`, `dsdb_update_gmsa_entry_keys()`, `dsdb_update_gmsa_keys()`, and `dsdb_gmsa_current_time()` expose rollover/update helpers.

## Control Flow

The header's contract splits gMSA operations into calculation and persistence. Callers can calculate an update with `gmsa_recalculate_managed_pwd()`, inspect returned password data if requested, then apply a prepared update through `dsdb_update_gmsa_entry_keys()` or let `dsdb_update_gmsa_keys()` process search results and signal retry.

## State and Persistence Behavior

`struct gmsa_update` intentionally stores both planned LDB requests and the password ID observed when planning. This enables compare-before-write behavior in the implementation. The `DSDB_GMSA_TIME_OPAQUE` macro defines an LDB opaque key for injecting current time in tests or controlled flows.

## Dependencies and Integration Points

The header depends on LDB, LDB modules, talloc, GKDI/GMSA crypto headers, `DATA_BLOB`, and Samba time types. It is consumed by DSDB modules that need to expose or maintain gMSA secrets.

## Risks

Because the header exposes raw password pointers in `gmsa_return_pwd` and update request pointers in `gmsa_update`, ownership and lifetime must be respected by callers. Any new secret attributes must be reflected in implementation redaction/update logic, not only in this contract.

## Test Signals

Compile tests should ensure C files include the header without circular dependency issues. Behavioral tests should validate all declared functions through `util.c`, especially update planning/application, operational password return, RODC handling, and time opaque injection.
