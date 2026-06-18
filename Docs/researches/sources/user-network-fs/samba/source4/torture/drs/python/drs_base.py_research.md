# sources/user-network-fs/samba/source4/torture/drs/python/drs_base.py Research

## Purpose
This file is the shared base library for Samba's Python DRS tests. It provides environment setup for two DCs, command helpers for `samba-tool drs`, DRS RPC bind helpers, raw `DsGetNCChanges` request builders, response validators, and linked-attribute comparison primitives.

## Important APIs, Types, And Functions
`DrsBaseTestCase.setUp()` enables GENSEC sealing, connects to `DC1` and `DC2`, and caches schema, domain, config, forest level, and DNS host names. Command helpers include `_run_drs_kcc()`, `_net_drs_replicate()`, and replication option toggles. Directory helpers include `_deleted_objects_dn()`, `_lost_and_found_dn()`, `_get_highest_hwm_utdv()`, and `_get_identifier()`.

DRS helpers include `_ds_bind()` for sealed DRSUAPI RPC binding, `_exop_req8()` and `_getnc_req10()` for request construction, `_get_replication()` for sending `DsGetNCChanges`, and `_check_replication()`/`_check_ctr6()` for validating returned DNs, links, counts, `more_data`, and errors. `AbstractLink` implements MS-DRSR link ordering and equality semantics using packed GUID blobs.

## Control Flow
Subclasses call setup, create directory state, then use base helpers either to run black-box `samba-tool drs` commands or issue raw DRSUAPI calls. Validation builds a request, sends `DsGetNCChanges`, extracts object DNs and linked attributes, filters intermittent RID Set changes, and compares ordered or unordered expectations.

## State And Persistence
The base stores DC connections and cached naming context state per test instance. It can mutate DC replication options and trigger replication, but does not create application objects by itself. `AbstractLink` stores packed GUID blobs for deterministic sorting and hashing.

## Dependencies And Integration Points
The file integrates Python Samba tests, LDB, generated DRSUAPI/misc/security/drsblobs types, NDR packing, GENSEC, Kerberos ccache command plumbing, and the SambaTool test base. It bridges high-level Python tests and low-level DRSUAPI protocol structures.

## Risks And Test Signals
Signals are successful sealed DRS binds, command success with empty stderr, exact CTR6 fields, and stable linked-attribute ordering. Risks include dependence on `DC1` and `DC2`, side effects from replication option helpers, possible directory churn affecting high-watermarks, and request defaults that can mask missing subclass setup.
