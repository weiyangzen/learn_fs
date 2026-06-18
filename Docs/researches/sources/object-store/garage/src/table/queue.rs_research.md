# sources/object-store/garage/src/table/queue.rs

Purpose: background worker that drains the local insert queue and republishes queued entries through normal table replication.

Important APIs and types: `InsertQueueWorker<F, R>(Arc<Table<F, R>>)` implements `garage_util::background::Worker`. `BATCH_SIZE` is 1024.

Control flow: `work` scans up to slightly over `BATCH_SIZE` entries from `data.insert_queue`, decodes them, calls `Table::insert_many` to replicate/apply them, and then removes queue rows only if their stored value still equals the processed value. `wait_for_work` wakes on either a 600 second timer or `insert_queue_notify`.

State and persistence: persistent state is the `insert_queue` DB tree. Compare-before-remove prevents losing a newer merged queued value that arrived while the batch was being processed.

Dependencies and integration: `TableData::queue_insert` writes this queue inside transactions and notifies after commit. The worker depends on table replication APIs, schema decoding, background worker status, Tokio select/watch, and queue approximate length for status.

Risks and test signals: if `insert_many` repeatedly fails, the queue remains and retries later. Decoding failures stop the worker iteration. Batching condition uses `> BATCH_SIZE`, so it may process 1025 entries. No direct tests; behavior depends on table insertion tests/integration.
