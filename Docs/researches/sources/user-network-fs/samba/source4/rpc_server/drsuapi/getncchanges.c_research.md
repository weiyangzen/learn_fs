# sources/user-network-fs/samba/source4/rpc_server/drsuapi/getncchanges.c

## Purpose
`getncchanges.c` implements the server side of `IDL_DRSGetNCChanges`, the core Active Directory replication RPC that returns changed objects, linked attributes, highwatermark progress, prefix mappings, and selected extended-operation results. It is the largest and most stateful part of this subset: normal replication can span multiple client calls, while extended operations such as RID allocation, object replication, secret replication, and FSMO owner changes are handled as special single-response cycles.

The file is responsible for translating LDB database records into DRSUAPI wire objects, enforcing replication access checks, filtering attributes through highwatermarks, uptodateness vectors, partial attribute sets, RODC filtered attribute behavior, and packaging linked attributes in Windows-compatible order. It also coordinates with `drsuapi_UpdateRefs()` when a client requests reference maintenance via replication flags.

## Important APIs, Types, and Functions
- `dcesrv_drsuapi_DsGetNCChanges()` is the public RPC handler. It pulls the DRS bind handle, normalizes request level 8 to level 10, checks source state and permissions, builds or resumes replication state, emits one chunk of objects and links, and updates output highwatermarks and UTD vectors.
- `struct drsuapi_getncchanges_state` is persistent replication-cycle state stored on `b_state->getncchanges_full_repl_state` for full replication. It tracks GUIDs to send, processed count, NC root identity, schema-NC status, GET_ANC/GET_TGT flags, min/max USNs, last/final highwatermarks, final UTD vector, linked attributes pending, and an optional object GUID cache.
- `struct getncchanges_repl_chunk` is per-call state. It caps object and link counts, tracks timeout budget, carries the linked list of response objects, and controls immediate linked-attribute emission.
- `get_nc_changes_build_object()` converts an LDB message into `drsuapi_DsReplicaObjectListItemEx`, loads `replPropertyMetaData`, filters changed attributes, converts LDAP syntax values into DRS attributes, applies secret processing/encryption, and validates attribute IDs.
- `get_nc_changes_filter_attrs()` implements attribute inclusion logic based on local USN, UTD vector, partial attribute set, RODC secret handling, RDN exclusion, and upgraded linked-attribute suppression.
- `get_nc_changes_add_links()` and `get_nc_changes_add_la()` collect forward linked attributes from extended DN values and build `drsuapi_DsReplicaLinkedAttribute` records with replication metadata.
- `getncchanges_get_sorted_array()` sorts linked attributes according to MS-DRSR CompareLinks ordering using NDR-form source/target GUIDs, attid, and active/deleted state.
- `getncchanges_add_ancestors()` and `getncchanges_chunk_add_la_targets()` support `DRSUAPI_DRS_GET_ANC` and `DRSUAPI_DRS_GET_TGT`, ensuring parent objects and linked-attribute targets are known to the client before dependent objects or links are sent.
- Extended-operation helpers include `getncchanges_rid_alloc()`, `getncchanges_repl_secret()`, `getncchanges_repl_obj()`, and `getncchanges_change_master()`.
- Permission classifiers `dcesrv_drsuapi_is_reveal_secrets_request()` and `dcesrv_drsuapi_is_gc_pas_request()` decide whether the request needs `GET_ALL_CHANGES` or can be satisfied by filtered-attribute rights.

## Control Flow
`dcesrv_drsuapi_DsGetNCChanges()` initializes the level-6 response, maps request revision 8 to request revision 10 when needed, creates a per-call chunk, rejects outbound replication from an RODC source, validates selected extended-operation destination DSA GUIDs, and requires `GUID_DRS_GET_CHANGES` on the request NC root. It then evaluates outbound replication disablement, partial attribute prefix maps, GC PAS access, and secret-reveal access. RODC callers have write-replication flags stripped.

The handler normalizes invocation-id and highwatermark semantics. A zero `source_dsa_invocation_id` is replaced with the local invocation id; a mismatched source invocation id resets the request highwatermark because the supplied HWM is not valid for this source. Full-sync requests discard the input UTD vector.

For ordinary replication, the handler may reuse `b_state->getncchanges_full_repl_state`. It invalidates that state if the caller switches NC roots or supplies a highwatermark different from the previous server output. There is a compatibility path for Entra ID Connect/Azure AD clients that zero `reserved_usn`; the code temporarily restores the saved value and continues only if the remaining highwatermark fields match.

When starting a new cycle, the handler resolves the naming context or extended-operation DN, verifies that ordinary replication targets an NC head, performs the requested extended-operation side effect if any, allocates `struct drsuapi_getncchanges_state`, and promotes it to bind-state lifetime only for non-extended full replication. It obtains the DCE/RPC session key for encrypted attributes.

Object collection happens once per replication cycle when `getnc_state->guids` is still unset. Normal replication searches for records with `uSNChanged >= min_usn + 1`, optionally applies a configured `drs:object filter`, critical-only filtering, base scope for async replication, or base scope for single-object exops. RID allocation uses a special collection path to return the RID Manager, the destination RID set, and destination server object in fixed order. Collected objects are reduced to GUID, DN, and USN, sorted by USN or by ancestor order for Samba 4.5 emulation, and stored as GUIDs to avoid holding full records across multiple calls.

Each call then prepares output naming-context data and prefix mappings, converts remote partial attribute sets into sorted local attids, optionally sends the NC root first, resumes pending GET_TGT linked-target checks, and loops over unsent GUIDs until object, link, or time limits are hit. Each GUID is re-searched by extended DN to fetch full current attributes. The object can be skipped if already sent as an ancestor. Otherwise it is built, added to the chunk, and its links are collected. The highwatermark advances only for messages whose `uSNChanged` is not greater than the cycle's initial maximum USN.

After object iteration, the handler sets object output fields, may call `drsuapi_UpdateRefs()` if requested by `DRSUAPI_DRS_ADD_REF` or `DRSUAPI_DRS_REF_GCSPN`, emits linked attributes either at the end of the cycle or immediately when configured/GET_TGT is active, and updates continuation state. Extended operations suppress final UTD and new-HWM output. Completed ordinary cycles return the final highwatermark and final UTD vector and then free the persistent state.

## State and Persistence Behavior
The file has two explicit state lifetimes. `struct getncchanges_repl_chunk` lives for one RPC call and enforces chunk size and work-time boundaries. `struct drsuapi_getncchanges_state` can persist across multiple full replication RPC calls on the DRS bind handle, holding the sorted GUID list, pending linked attributes, last returned highwatermark, and object cache.

Persistent state is deliberately not touched by extended operations. The comments call out that Azure AD Connect can interleave `REPL_OBJ` with full replication, so exops are treated as single-response cycles that must not reset the full replication cursor. On final ordinary response, the state is stolen to the per-call memory context and `b_state->getncchanges_full_repl_state` is cleared.

Database persistence occurs in several places. Secret replication can update `msDS-RevealedUsers` on the destination machine account inside an LDB transaction. RID allocation invokes the `DSDB_EXTENDED_ALLOCATE_RID_POOL` extended operation in a transaction. FSMO owner transfer modifies `fSMORoleOwner` in a transaction. `drsuapi_UpdateRefs()` can persist `repsTo` changes when a GetNCChanges request asks to add replication references.

The object cache for GET_ANC/GET_TGT uses `db_open_rbt()` and stores serialized GUID keys via dbwrap. It is per-replication-cycle memory-backed state, not durable storage.

## Dependencies and Integration Points
The code sits at the intersection of DCE/RPC, Samba DSDB, LDB, schema conversion, security, and replication services. It includes generated NDR DRSUAPI and DRS blob definitions, DSDB schema and utility APIs, security token helpers, DRS client utilities, dbwrap, sorting helpers, and the DCE/RPC server framework.

Key DSDB/LDB integrations include `drsuapi_search_with_extended_dn()`, `dsdb_search_dn()`, `drs_ObjectIdentifier_to_dn_and_nc_root()`, `dsdb_get_schema()`, `dsdb_get_oid_mappings_drsuapi()`, `dsdb_load_udv_v2()`, `dsdb_loadreps()`, and syntax-specific `ldb_to_drsuapi()` conversion functions. Security integration is through `drs_security_access_check_nc_root()`, `drs_security_access_check()`, session-token user levels, `samdb_rodc()`, and DRS extended rights GUIDs.

Replication side effects integrate with `updaterefs.c` through `drsuapi_UpdateRefs()`. Password/secret handling integrates with `drsuapi_encrypt_attribute()`, `drsuapi_process_secret_attribute()`, the DCE/RPC session key, RODC filtered attribute set helpers, and `samdb_confirm_rodc_allowed_to_repl_to()`.

## Risks and Edge Cases
- This is security-sensitive code. Incorrect classification of secret requests, GC PAS requests, or partial attribute mappings can leak secret attributes or deny legitimate replication.
- Highwatermark continuity is subtle. The file intentionally detects stale or unexpected continuation highwatermarks, but also carries an Azure AD compatibility exception for zeroed `reserved_usn`; changes here can break replication paging or cause duplicates/loss.
- The object list is collected once as GUIDs and then each object is re-searched later. That reduces memory but creates race windows with tombstone expunge or concurrent changes. The code skips disappeared objects but must avoid advancing the HWM past unseen changes.
- Linked attribute processing depends on upgraded link metadata in extended DNs. Missing `RMD_*` components, hanging targets, recycled targets, or inconsistent `uSNChanged` versus `RMD_LOCAL_USN` can cause internal errors or skipped links.
- GET_ANC and GET_TGT use a per-cycle object cache to avoid duplicate sends. Cache misuse can omit necessary ancestors or targets, while disabling the Samba 4.5 emulation changes ordering expectations.
- Secret replication both returns sensitive data and writes `msDS-RevealedUsers`. Transaction handling must keep the audit trail consistent with what is sent.
- Configured limits (`drs:max object sync`, `drs:max link sync`, `drs:max work time`, immediate link sync, object filter, GET_TGT support) directly affect paging behavior and interoperability.
- Several TODOs and comments admit imperfect behavior, including NC size reporting and incomplete extended-operation support.

## Test Signals
Useful tests should exercise normal multi-page replication with stable HWM/UTD progression, a stale highwatermark restart, the Azure AD `reserved_usn` compatibility path, prefix-map and partial-attribute-set conversion, GC PAS-only requests, and secret-request denial/allowance for RWDC and RODC callers. Linked-attribute tests should cover active/deleted links, recycled targets, hanging targets, sort order, immediate link sync, GET_TGT target inclusion, and GET_ANC ancestor ordering. Extended-op tests should cover RID allocation success/failure, FSMO owner transfer errors, `REPL_OBJ`, `REPL_SECRET`, outbound replication disabled, and RODC source rejection. Regression tests should verify that interleaved exops do not clear an in-progress full replication state.
