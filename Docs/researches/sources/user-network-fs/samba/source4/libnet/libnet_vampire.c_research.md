# sources/user-network-fs/samba/source4/libnet/libnet_vampire.c

## Purpose

`libnet_vampire.c` contains default callbacks for the Samba4 "vampire"/BecomeDC replication path: provision a bare local AD database, receive DRS replication chunks from a source DC, resolve/apply the remote schema, convert replicated objects, and commit them into local LDB/DSDB with replication metadata.

## Important APIs, Types, and Functions

State is held in private `struct libnet_vampire_cb_state`, which tracks names, credentials, schemas, prefix map, LDB, schema chunk accumulation, target directory, loadparm/event contexts, debug counters, and server DN.

Exported callback helpers:
- `libnet_vampire_replicate_init()` initializes replication chunk state around an existing `samdb`.
- `libnet_vampire_cb_state_init()` builds callback state for BecomeDC tests/flows.
- `libnet_vampire_cb_ldb()` and `libnet_vampire_cb_lp_ctx()` expose the resulting LDB/loadparm.
- `libnet_vampire_cb_prepare_db()` provisions a bare database with `provision_bare()` and starts an LDB transaction.
- `libnet_vampire_cb_check_options()` logs BecomeDC source/destination options.
- `libnet_vampire_cb_schema_chunk()` accumulates schema DRS objects and calls `libnet_vampire_cb_apply_schema()` at end of partition.
- `libnet_vampire_cb_store_chunk()` converts and commits normal config/domain/application chunks.

## Control Flow

Preparation creates a bare database using naming information from BecomeDC, a random machine password, and NTVFS-enabled provision settings, then starts one transaction around the full vampire operation so linked-attribute backlinks can be resolved at commit.

Schema flow strips schema-info from the remote prefix map for local provision reload, initializes a self-made schema, appends incoming schema chunk linked lists until `more_data` is false, resolves a working schema through `dsdb_repl_resolve_working_schema()`, attaches it to LDB, converts objects with `dsdb_replicated_objects_convert()`, commits them, writes `prefixMap`, and reloads the schema.

Normal chunk flow decodes level-1 or level-6 DRS replies and request levels 0/5/8/10, derives replication flags for exops, critical-only, GET_TGT, full sync, and special-secret processing, converts replicated objects against the current schema, optionally dumps LDIF/debug metadata, commits objects, and validates linked-attribute identifiers for debug output.

## State and Persistence Behavior

This file writes an entire local AD database under the provision target. It persists schema, configuration/domain objects, replication metadata, prefixMap, repsFromTo metadata, high-watermarks when appropriate, and linked attributes via DSDB commit hooks. The long transaction is essential state behavior. It also tracks per-partition object/link counts and clears counters when a partition finishes.

## Dependencies and Integration Points

It integrates with BecomeDC callbacks, DRSUAPI generated structures, DSDB schema/prefix-map/replication conversion APIs, LDB transactions and LDIF writing, provisioning, loadparm configuration knobs (`become dc:dump objects`, `schema convert retrial`), security/session key handling, and Python replication bindings in `py_net.c`. `source4/torture/libnet/libnet_BecomeDC.c` wires these callbacks into a promotion test.

## Risks and Edge Cases

Schema handling is delicate: remote prefix maps, schemaInfo stripping, two-phase conversion, and schema attachment must remain consistent. Chunk-level request/response version handling must preserve high-watermark correctness while avoiding recording incomplete critical-only or exop subsets. Incorrect DSDB replication flags can mishandle secrets or linked attributes. The transaction must be committed by higher-level code; failure or abort can leave provisioned files needing cleanup. Debug dumping may expose sensitive replicated data.

## Test Signals

BecomeDC/vampire integration tests are the strongest signal: schema partition import, config/domain chunk import, linked-attribute backlink correctness after transaction commit, prefixMap presence, secret-processing behavior, exop/critical-only behavior, and Python `replicate_chunk()` paths. Negative tests should inject bad prefix maps, unsupported ctr/request levels, missing schema, conversion failures, and commit failures.
