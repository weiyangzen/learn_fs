# sources/user-network-fs/samba/source4/torture/drs/python/getnc_exop.py Research

## Purpose
This module is a broad semi-black-box test suite for `DsGetNCChanges` extended operations, prefix-map handling, linked-attribute return ordering, ancestor and target flags, FSMO error paths, and partial attribute set behavior. It aims to keep Samba compatible with Windows DRSUAPI edge cases.

## Important APIs, Types, And Functions
`_linked_attribute_compare()` implements MS-DRSR linked-attribute ordering for raw DRS link structures. `DrsReplicaSyncTestCase` covers EXOP behavior and invalid inputs, using `_determine_fSMORoleOwner()`, `_check_exop_failed()`, and inherited request/response helpers. `DrsReplicaPrefixMapTestCase` verifies missing prefix maps, invalid attids, secret `unicodePwd`, regular `name`, and `partial_attribute_set_ex`; `_samdb_fetch_pfm_and_schi()` reads `prefixMap` and `schemaInfo` and appends schema-info mapping. `DrsReplicaSyncSortTestCase` validates linked-attribute order for single-object and whole-NC replication.

## Control Flow
The sync tests create a random OU, bind to DC1 by DRS RPC, and capture default high-watermark and UTD vector state. Single-object tests assert `DRSUAPI_EXOP_REPL_OBJ` returns only the requested object even with `GET_ANC` or `GET_TGT`. Invalid NC/GUID tests construct request8 payloads with dummy DNs and invalid or valid GUIDs. `test_link_utdv_hwm()` progressively creates nested OUs, a disabled computer, containers, and `managedBy` links, then repeats replication checks under combinations of `WRIT_REP`, `CRITICAL_ONLY`, `GET_ANC`, `GET_TGT`, high-watermark, and UTD-vector inputs.

FSMO tests send EXOP FSMO requests to owner and non-owner DCs and validate extended return codes. Prefix-map tests request attributes through normal and modified mappings to ensure incoming attids are mapped or rejected correctly. Sort tests compare returned linked attributes to local expected ordering before and after one link becomes inactive.

## State And Persistence
The module creates random OUs, users, groups, computer objects, containers, and linked attributes on DC1, then deletes test OUs with `tree_delete:1` in teardown. High-watermarks and UTD vectors are used as state checkpoints for incremental queries. Failures can leave temporary directory objects and changed links.

## Dependencies And Integration Points
The suite depends on `drs_base`, LDB, generated DRSUAPI and misc types, NDR packing/unpacking, `drs_DsBind`, werror values, and two DCs for FSMO owner decisions. It is tightly integrated with DRS request levels 8 and 10 and schema prefix-map encoding.

## Risks And Test Signals
Signals include exact WERROR exceptions, level 6 responses, `extended_ret`, source DSA GUID/invocation ID, object DN order, linked attribute count/order, `more_data`, NC counts, and returned attids. Risks include high scenario complexity, documented Windows/Samba differences, broad exception handling while unpacking link targets, random object cleanup, and sensitivity to unrelated directory churn.
