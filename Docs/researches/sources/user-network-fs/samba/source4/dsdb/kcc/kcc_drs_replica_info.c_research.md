# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_drs_replica_info.c

## Purpose

`kcc_drs_replica_info.c` implements the KCC IRPC handler for `DsReplicaGetInfo`. It builds responses for selected DRS replication information types: inbound neighbors, outbound repsTo neighbors, up-to-date cursors, pending operations, and object metadata version 2. Many other info types are explicitly not supported.

## Important APIs, Types, and Functions

- `get_linked_attribute_value_stamp()` reads extended metadata (`RMD_VERSION`, `RMD_CHANGETIME`, `RMD_ORIGINATING_USN`) for a linked attribute value.
- `get_repl_prop_metadata_ctr()` reads and NDR-decodes `replPropertyMetaData`.
- `get_dn_from_invocation_id()` finds an `nTDSDSA` DN by `invocationId`.
- `kccdrs_replica_get_info_obj_metadata2()` returns per-attribute metadata, with optional linked-attribute stamp improvement for active forward links.
- `kccdrs_replica_get_info_cursors()` and `kccdrs_replica_get_info_cursors2()` load up-to-date vectors via `dsdb_load_udv_v1()` and `dsdb_load_udv_v2()`.
- `kccdrs_replica_get_info_pending_ops()` returns a timestamped empty pending-ops list.
- `get_master_ncs()` and `get_ncs_list()` build naming-context lists from `msDS-hasMasterNCs`/`hasPartialReplicaNCs` or a requested object DN.
- `copy_repsfrom_1_to_2()` converts version 1 reps blobs into version 2 shape.
- `fill_neighbor_from_repsFrom()` and `fill_neighbor_from_repsTo()` populate `drsuapi_DsReplicaNeighbour` records.
- `kccdrs_replica_get_info_neighbours()` and `kccdrs_replica_get_info_repsto()` enumerate `repsFrom` and `repsTo` blobs.
- `kccdrs_replica_get_info()` validates request level, dispatches by info type, fills the output info type/result, and returns `NT_STATUS_OK` for IRPC transport.

## Control Flow

The handler accepts request levels `DRSUAPI_DS_REPLICA_GET_INFO` and `DRSUAPI_DS_REPLICA_GET_INFO2`. Level 1 starts at base index zero; level 2 honors `enumeration_context` and returns `WERR_NO_MORE_ITEMS` for `0xffffffff`. It chooses `info_type`, optional object DN, source DSA GUID, and base index, then dispatches.

Neighbor enumeration builds an NC list. If an object DN is supplied, it uses only that DN. Otherwise, it searches the local nTDSDSA object by service `ntds_guid` and reads hosted master/partial NC attributes. For each NC, it loads `repsFrom` or `repsTo`, normalizes version 1 to version 2 if needed, filters inbound neighbors by requested source DSA GUID when provided, applies base-index pagination, and appends populated neighbor records. Neighbor population resolves source DSA and transport GUIDs to DNs, fills NC GUIDs, high-watermarks, attempt/success timestamps, result codes, and failure counts.

Object metadata reads `replPropertyMetaData`, maps attribute IDs to schema names, optionally improves forward-link metadata using link value stamps for level 2 requests with active linked-attribute flags, applies base index, resolves originating invocation IDs to DSA DNs, and fills `DsReplicaObjMetaData2` entries.

Cursor responses validate the DN and load UDV v1/v2. Pending ops reports no pending operations with the current timestamp.

## State and Persistence Behavior

The file is read-only. It exposes replication state persisted in `replPropertyMetaData`, up-to-date vectors, hosted NC attributes, `repsFrom`, `repsTo`, object GUIDs, invocation IDs, and extended linked-value metadata. It allocates response structures on a request memory context and stores only the WERROR in the outgoing IRPC result.

## Dependencies and Integration Points

It integrates with KCC service private data, DRSUAPI generated types, DSDB replication metadata helpers, schema lookup, GUID/DN resolution, reps blob loaders, UDV loaders, and IRPC. It is part of the KCC service's DRS management surface.

## Risks

Several paths log at level 0 and return generic internal errors, which can be noisy or opaque. `get_linked_attribute_value_stamp()` appears to write `RMD_ORIGINATING_USN` into `attr_version` rather than `attr_orig_usn`, which would lose the actual originating USN in improved metadata; this deserves focused review. Object metadata indexing uses `attr = &array[j]` while looping `i`, so skipped/base-index logic should be checked carefully for off-by-one behavior. Many info types are unsupported, which may affect interoperability. DN construction from caller-supplied object strings must rely on LDB validation paths.

## Test Signals

Tests should cover both request levels, enumeration context handling, unsupported info types, inbound/outbound neighbor enumeration with version 1 and version 2 reps blobs, source GUID filtering, base-index pagination, missing source/transport DN resolution, UDV v1/v2 success and bad NC errors, empty pending ops, object metadata for normal and linked attributes, invocation-ID-to-DN failures, malformed `replPropertyMetaData`, and the suspected `RMD_ORIGINATING_USN` assignment bug.
