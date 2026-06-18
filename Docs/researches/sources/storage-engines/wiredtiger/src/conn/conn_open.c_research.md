# sources/storage-engines/wiredtiger/src/conn/conn_open.c

## Purpose
This file orchestrates major connection open, worker startup, and connection close ordering. It wires together the cache, eviction, transaction, recovery, logging, metadata, disaggregated storage, tiered storage, statistics, sweep, checkpoint, prefetch, and cleanup subsystems.

## Important APIs, Types, and Functions
The main entry points are `__wti_connection_open`, `__wti_connection_close`, and `__wti_connection_workers`. They operate on `WT_CONNECTION_IMPL`, its default/internal sessions, connection flags, server flags, and subsystem-owned state.

## Control Flow and Behavior
Open allocates the session array, opens the default internal session, publishes the initialized connection pointer with a release barrier, creates cache/eviction/shared-cache state, initializes transaction and rollback-to-stable state, records dhandle stat sizing, and configures load control after cache and eviction are available.

Worker startup begins with checkpoint reconciliation threads and statistics logging, detects disaggregated mode from `disaggregated.page_log`, starts tiered storage unless disaggregated is enabled, creates the log manager, configures page history, runs recovery, starts live restore, initializes metadata tracking, configures disaggregated storage, opens the history store, opens logging, starts eviction, sweep, background compact, capacity, checkpoint, prefetch, and checkpoint cleanup.

Close sets `WT_CONN_CLOSING`, restores data-handle access on the default session, then shuts down subsystems in dependency order: page history, live restore, background compact, checkpoint, stats, tiered, sweep, prefetch, parallel checkpoint, eviction threads, capacity, data handles, metadata tracking, block cache, layered table manager, log manager, disaggregated storage, extensions, shared cache, eviction, cache, transactions, files, optrack, backup metadata, sessions, file system, dynamic libraries, compiled config, and finally the connection object.

## State and Persistence
This file coordinates both volatile and persistent state. It ensures recovery runs before history-store creation and before eviction threads, ensures logging is open before operations that may commit, and checkpoints log state on close when logging recovery is complete. It also removes backup temp state and releases lock/optrack files.

## Dependencies and Integration Points
It is the high-level integration point for nearly every connection subsystem. Ordering constraints are encoded directly in the call sequence, including disaggregated/tiered mutual exclusion, metadata/disaggregated/history-store order, and eviction shutdown after all higher-level servers stop.

## Risks
Risks are mostly ordering regressions: starting eviction before history store exists, running tiered storage in disaggregated mode, closing data handles before worker threads stop, destroying cache before shared-cache disconnect, closing log manager before checkpoint-log stop, or leaving sessions and hazard/stash state allocated on close.

## Test Signals
Signals include connection open/close smoke tests, recovery tests, leak checks, tiered/disaggregated mode combinations, logging shutdown tests, backup cleanup tests, and tests that enable optional servers such as stats, sweep, prefetch, checkpoint, and page history.
