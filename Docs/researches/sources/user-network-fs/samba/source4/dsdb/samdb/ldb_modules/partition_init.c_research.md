# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_init.c

## Purpose

`partition_init.c` initializes and refreshes the Samba DSDB partition module's backend list. It reads the `@PARTITION` record, parses partition DNs, replicate entries, per-partition module chains, partial-replica markers, and backend store type, opens backend databases, loads their module chains, registers partitions with rootDSE, and implements the extended operation used to create a new partition.

This file converts persistent partition metadata into the runtime `partition_private_data` that `partition.c` uses for routing and locking.

## Important APIs and Functions

`partition_load_replicate_dns()` parses the `replicateEntries` attribute into validated `ldb_dn` objects for special records that should be copied to every partition.

`partition_load_modules()` parses `modules` values of the form `DN:module,list` or `*:module,list` into `partition_module` entries. `find_modules_for_dn()` later selects the exact DN module list or the default list.

`partition_reload_metadata()` searches `@PARTITION` for `partition`, `replicateEntries`, `modules`, `partialReplica`, and `backendStore`, then refreshes replicate and module mappings. It can use a forced module message from the Samba4 wrapper instead of DB-stored module declarations.

`new_partition_from_dn()` creates a `dsdb_partition`: it computes a relative backend path, creates the backend directory when writable, builds the backend URL, connects the backend, loads the configured module list, initializes the chain, wraps it in a synthetic `partition_next` module, and starts a transaction on the new backend if the partition module is already in a transaction.

`add_partition_to_data()` appends a partition, sorts the partition list by DN, and registers the partition with rootDSE through `partition_register()`.

`partition_reload_if_required()` compares the primary sequence number with cached `metadata_seq`; when changed, it initializes metadata TDB, reloads `@PARTITION`, creates any newly declared partitions, detects partial replicas, and preserves canonical DN case by searching the new backend root.

`new_partition_set_replicated_metadata()` copies configured special metadata records from the main partition into a new backend, replacing existing records when necessary.

`partition_create()` handles `DSDB_EXTENDED_CREATE_PARTITION_OID`: it adds a new `partition` value to `@PARTITION`, optionally records `partialReplica`, creates the backend, copies replicated metadata, and inserts the new runtime partition.

`partition_init()` performs initial reload, registers domain-scope and search-options controls, and then calls the next module init.

## Control Flow

Reload is sequence-driven. `partition_reload_if_required()` obtains the primary sequence number and returns early if unchanged. On change, it ensures `metadata.tdb` exists, reads `@PARTITION`, refreshes metadata fields, and iterates `partition` attribute values. Existing partitions are skipped first by exact original record blob comparison and then by DN comparison.

Partition values can include an explicit `DN:filename.ldb` suffix. Without a filename, the code generates one from the DN, using plain DN text only for a narrow safe character set and base64 encoding otherwise. `partition_create()` uses a similar but URL-escaped filename under `sam.ldb.d/`.

After opening a new backend, the code searches the backend root with no attrs. If found, it replaces the control DN with the case-preserved DN from the database. It then marks partial replicas based on `partialReplica` values and adds/registers the partition.

The create-partition extended operation first reloads metadata to avoid stale state, checks whether the partition already exists, modifies `@PARTITION` if needed, creates the backend runtime object, copies replicated metadata, and only then publishes it into the module-private partition array.

## State and Persistence Behavior

Persistent inputs are the `@PARTITION` record and the backend databases it names. Persistent writes occur when `partition_create()` modifies `@PARTITION` and when `new_partition_set_replicated_metadata()` populates records in a newly created backend. `partition_reload_if_required()` also initializes `sam.ldb.d/metadata.tdb` through `partition_metadata_init()` if it is missing.

Runtime state is talloc-owned by `partition_private_data`. `metadata_seq` tracks the primary DB sequence that last drove reload. `orig_record` stores the exact partition attribute value to distinguish already loaded partition records.

If reload or creation happens while a global transaction is active, `new_partition_from_dn()` starts a transaction on the new backend so later transaction end/abort calls remain balanced.

## Dependencies and Integration Points

The file depends on DSDB module search helpers, LDB backend connection/loading APIs, generated module-list parsing, rootDSE partition registration, `ldb_relative_path()`, loadparm-backed backend options, `ldb_wrap.h`, filesystem directory creation, URL/base64 escaping helpers, and partition metadata helpers.

It is coupled to `partition.c` through sorted partition ordering and to `partition_metadata.c` through sequence-driven reload and metadata TDB initialization.

## Risks and Edge Cases

Parsing `@PARTITION` is sensitive. Invalid DNs, malformed `modules` records without `:`, unsafe filenames, or missing module mappings fail initialization/reload. Since partitions can be discovered during locks/transactions, failure paths must preserve transaction balance.

Filename generation intentionally avoids shell metacharacters and path traversal. Changes here need security review because partition values ultimately influence backend paths.

`partition_reload_if_required()` only adds new partitions; it does not remove partitions whose metadata disappeared. That may be deliberate for long-lived process safety, but it matters for any future dynamic removal work.

The initial metadata TDB migration path creates the DB but relies on later sequence increment logic to populate sequence values. Sequence-number consumers must tolerate zero.

`new_partition_set_replicated_metadata()` performs delete/re-add replacement for existing replicated metadata. Midway failures can leave a new partition partially initialized unless enclosed by transaction behavior.

## Test Signals

Tests should cover valid and invalid `@PARTITION` parsing, explicit and generated backend filenames, module mapping with exact DN and default `*`, forced module messages, reload no-op when sequence is unchanged, discovering a new partition after sequence change, partial-replica marking, canonical DN case replacement, rootDSE registration, create-partition with and without partial-replica control, copied replicated metadata including replacement of existing records, transaction-active partition creation, read-only initialization, and error paths for missing backend modules or invalid replicate DNs.
