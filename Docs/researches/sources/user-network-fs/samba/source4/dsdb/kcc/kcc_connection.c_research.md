# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.c

## Purpose

`kcc_connection.c` manages generated `nTDSConnection` objects for the KCC service. It finds existing inbound replication connection objects under the local NTDS Settings object, compares them with desired DSA connection entries, adds missing generated connections, and deletes obsolete ones.

## Important APIs, Types, and Functions

- `kccsrv_add_connection()` creates a new `nTDSConnection` child under the local NTDS Settings DN, names it with a random GUID, resolves the source server DN from `conn->dsa_guid`, sets required attributes, and marks `options` with `NTDSCONN_OPT_IS_GENERATED`.
- `kccsrv_delete_connection()` finds an existing connection object by `conn->obj_guid` and deletes it.
- `kccsrv_apply_connections()` reconciles an existing NTDS connection list with a desired DSA list by deleting missing entries and adding absent desired entries.
- `kccsrv_find_connections()` searches one level below local NTDS Settings for `objectClass=nTDSConnection`, extracts each connection object's GUID, resolves the `fromServer` DN to a DSA GUID, and returns a `struct kcc_connection_list`.

## Control Flow

Discovery starts at `samdb_ntds_settings_dn()` and performs an LDB one-level search for `nTDSConnection` objects with `objectGUID` and `fromServer`. Each result records the connection object's GUID and the source DSA GUID. Entries whose `fromServer` cannot be resolved are logged and skipped.

Reconciliation first iterates existing NTDS connections and deletes those whose `dsa_guid` is absent from the desired DSA list. It then iterates desired DSA connections and creates any whose `dsa_guid` is absent from the existing list. Add operations build a new child DN, resolve `fromServer`, set `objectClass`, `showInAdvancedViewOnly`, `enabledConnection`, `fromServer`, and generated `options`, then call `ldb_add()`.

## State and Persistence Behavior

The file persists additions and deletions of `nTDSConnection` objects in the configuration partition. It does not create explicit transactions around the whole reconciliation. The returned connection list is talloc-owned by the caller. The `schedule` field exists in the data type but schedule writes are commented out in add logic.

## Dependencies and Integration Points

It depends on KCC service state (`struct kccsrv_service`), samdb NTDS Settings helpers, GUID/DN resolution helpers, generated DRS constants, LDB add/delete/search, and the connection structures declared in `kcc_connection.h`.

## Risks

The file has an explicit FIXME: `kccsrv_apply_connections()` does not respect administrator-created connections whose generated option bit is not set. As written, it can delete any existing connection absent from the desired list, regardless of whether it was generated. Lack of transaction means a reconciliation can partially add/delete. Add uses random GUID names and does not populate schedule. Desired-list null handling is asymmetric: deletion assumes `dsa_list` is non-NULL.

## Test Signals

Tests should cover discovery with valid and invalid `fromServer`, add attribute content and generated option, delete by object GUID, no-op when lists match, delete obsolete generated connections, add missing desired connections, behavior when existing list is NULL, and the admin-created connection risk once fixed.
