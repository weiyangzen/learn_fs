# sources/storage-engines/wiredtiger/src/schema/schema_publish.c

Purpose: publishes table or layered schema changes at a requested disaggregated schema epoch.

Important APIs and functions: `__wt_schema_publish` parses `disaggregated.schema_epoch` from session publish config and calls the internal `__schema_publish_disagg_schema_epoch`.

Control flow: publishing requires the schema lock. The internal helper rejects epoch zero, rejects non-disaggregated connections, takes the transaction-global read lock to synchronize with stable schema epoch advancement, checks that the requested epoch is newer than any stable schema epoch, and queues publication by stripped table/layered name. Only `table:` and `layered:` URIs are supported.

State and persistence behavior: this file does not directly mutate local metadata. It enqueues shared metadata publication work through `__wt_disagg_shared_metadata_queue_publish`; that queue is the durable/integration path for disaggregated shared metadata visibility.

Dependencies and integration points: depends on schema lock ownership, transaction-global rwlock ordering, stable disaggregated schema epoch accessors, timestamp parsing, disaggregated connection detection, and shared metadata queue APIs.

Risks: publishing with an epoch older than the stable schema epoch would expose stale schema state and is explicitly rejected. Lock ordering must remain table/schema lock before transaction-global read lock. Unsupported URI types must fail clearly because only table/layered shared metadata names are enqueued.

Test signals: publish with zero epoch, older/equal/newer epochs, non-disaggregated connections, table and layered URI success, unsupported URI failure, and races with stable schema epoch advancement.
