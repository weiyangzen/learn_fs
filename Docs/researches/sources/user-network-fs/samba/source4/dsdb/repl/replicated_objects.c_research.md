# sources/user-network-fs/samba/source4/dsdb/repl/replicated_objects.c

## Purpose
`replicated_objects.c` converts DRS replication wire objects into Samba DSDB/LDB messages and commits them transactionally. It is the bridge between `drsuapi_DsReplicaObjectListItemEx` / linked-attribute replication data and the local `DSDB_EXTENDED_REPLICATED_OBJECTS_OID` extended operation. It also builds temporary "working schema" views needed while the schema naming context is itself being replicated.

## Important APIs, types, and functions
- `dsdb_repl_make_working_schema()` shallow-copies the current schema, merges the remote prefix map, and resolves incoming schema objects into a temporary schema cache.
- `dsdb_repl_resolve_working_schema()` performs multi-pass conversion of replicated schema objects, retrying objects whose dependencies are not yet available.
- `dsdb_convert_object_ex()` validates one replicated object, decrypts secret attributes, converts DRS attributes to LDB elements, builds `replPropertyMetaDataBlob`, validates RDN/name consistency, adjusts partial replica `instanceType`, and returns a `dsdb_extended_replicated_object`.
- `dsdb_replicated_objects_convert()` converts a full replication response, including linked attributes, source DSA state, uptodateness vector, partition DN, and replication flags into `dsdb_extended_replicated_objects`.
- `dsdb_replicated_objects_commit()` wraps application of converted objects in an LDB transaction, swaps in a working schema while needed, runs schema validation, commits, updates notify USN behavior, and reloads the committed schema.
- `dsdb_origin_objects_commit()` handles originating object adds for non-Ex `drsuapi_DsReplicaObjectListItem`, optionally creating partial replica NCs before adds.

Key data types include `dsdb_schema`, `dsdb_schema_prefixmap`, `drsuapi_DsReplicaObjectListItemEx`, `drsuapi_DsReplicaLinkedAttribute`, `dsdb_extended_replicated_object`, `dsdb_extended_replicated_objects`, and `replPropertyMetaDataBlob`.

## Control flow
Schema replication starts with `dsdb_repl_make_working_schema()`: copy the initial schema, mark resolving in progress, decode the remote prefix map, merge missing OID prefixes into the local copy, and call `dsdb_repl_resolve_working_schema()`. Resolution builds a linked list of incoming schema objects and repeatedly tries `dsdb_convert_object_ex()` plus `dsdb_schema_set_el_from_ldb_msg_dups()`. When a pass succeeds for at least one object, it removes those list entries; when no object can be converted, it fails to avoid an infinite loop. After enough progress, it switches from the initial/bootstrap schema to the resulting schema and rebuilds sorted schema accessors.

Normal object conversion starts in `dsdb_replicated_objects_convert()`. It references the schema into the output lifetime, decodes the remote prefix map, checks remote schema compatibility when not replicating the schema NC, then iterates the DRS object linked list. Each object is converted by `dsdb_convert_object_ex()`. Objects outside the requested partition that are NC heads are ignored with `WERR_DS_ADD_REPLICA_INHIBITED`; all other conversion failures abort the batch. The function then deep-copies linked attributes enough for local ownership, translates remote ATTIDs to local ATTIDs, and returns the prepared extended operation payload.

Commit uses `ldb_transaction_start()`, records the partition USN before apply, optionally installs the working schema into the LDB context, and calls `ldb_extended(... DSDB_EXTENDED_REPLICATED_OBJECTS_OID ...)`. For schema replication it writes the new prefix map to LDB and uses `DSDB_EXTENDED_SCHEMA_LOAD` before `ldb_transaction_prepare_commit()` to catch corrupt schema writes within the same transaction. After commit it suppresses notification USN advancement only when the inbound apply caused originating updates or an earlier notification was already pending, then reloads/makes global the schema as appropriate.

## State and persistence behavior
The conversion layer allocates output trees with talloc ownership under the returned `dsdb_extended_replicated_objects`. Converted messages hold DNs, attribute elements, `when_changed`, parent GUIDs, object GUIDs, replication flags, source DSA pointers, uptodateness vectors, and linked attributes. Persistent database changes happen only in commit functions: replicated objects are applied by the DSDB extended operation inside an LDB transaction; schema prefix map updates are written before transaction prepare; originating objects are added with relaxed controls inside their own transaction and then re-read for assigned GUID/SID output.

Working schema state is deliberately memory-only during conversion and commit. The previous schema reference/global schema mode is restored on failures. After a successful schema commit, the schema is reloaded from the database rather than continuing to use the working copy.

## Dependencies and integration points
This file depends on DRSUAPI generated NDR types, DSDB schema helpers, prefix-map helpers, DRS attribute decrypt/convert helpers, LDB transactions/extended operations, security key material for secret decryption, and partition USN helpers. It integrates with `repl_meta_data`/DSDB extended operations via `DSDB_EXTENDED_REPLICATED_OBJECTS_OID`, with schema reload via `DSDB_EXTENDED_SCHEMA_LOAD`, and with notification logic through the caller-supplied `notify_uSN`.

## Risks and edge cases
- Input validation is strict: missing identifiers, missing DNs, metadata count mismatches, duplicate/missing `instanceType`, zero originating invocation IDs, and RDN/name mismatches all fail.
- Secret handling relies on `drsuapi_decrypt_attribute()` and treats `WERR_TOO_MANY_SECRETS` as suspicious server behavior.
- Prefix-map conversion is critical because stored replication metadata must contain local ATTIDs, not remote host-specific ATTIDs.
- Partial replica handling removes `INSTANCE_TYPE_WRITE`; read-write replication rejects sources that do not advertise writeable objects.
- Schema commit has many restore paths; any future change must preserve previous schema restoration on all transaction failures.
- The code tolerates duplicate schema objects by keeping the last resolved schema element, but a no-progress pass is fatal.

## Test signals
Relevant tests should exercise inbound replication of normal objects, schema NC replication with interdependent class/attribute ordering, remote prefix-map changes, linked attribute ATTID conversion, RODC/partial replica `instanceType` behavior, object outside partition skipping, zero invocation ID rejection, RDN/name mismatch rejection, transaction rollback on extended operation failure, schema reload after commit, and originating object add/partial NC creation paths.
