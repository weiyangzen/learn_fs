# sources/storage-engines/wiredtiger/test/suite/test_layered_config14.py

Purpose: comprehensive restart-without-local-files test for layered/shared metadata reconstruction, ingest/stable metadata presence, reads before/after step-up, continued writes, checkpointing, and a second restart.

Important APIs/types/functions: helpers `check_metadata_cursor` and `check_shared_metadata`; uses `metadata:` cursor, `file:WiredTigerShared.wt_stable` cursor, `restart_without_local_files(pickup_checkpoint=False)`, checkpoint metadata reconfigure, role reconfigure, and mixed URI sets: layered table URIs, disagg file URI, and disagg table URI.

Control flow: leader creates all URIs with appropriate disaggregated/log config, writes 500 rows each, checkpoints, and records checkpoint metadata. Restart 1 steps down, restarts without local files and without pickup, verifies no shared URIs in local metadata, picks up metadata, verifies shared/local metadata including ingest files, reads all tables before and after step-up, updates selected URIs, verifies leader reads before checkpoint, checkpoints, verifies metadata and values, steps down, restarts again without local files, picks up latest metadata, steps up, and verifies metadata and values again.

State and persistence behavior: exercises shared metadata table content, local metadata reconstruction, ingest/stable file metadata, table data, and updates across multiple restarts. Some URIs are updated while others must remain unchanged.

Dependencies/integration points: checkpoint metadata pickup, shared metadata table, local metadata population, restart cleanup, role transition, and layered/shared table handling.

Risks: long scenario with many assertions; failure diagnosis may require locating which restart/metadata phase broke. Set-derived `same_uris` can produce nondeterministic iteration order but assertions are order-independent.

Test signals: pass means a node can start without local files, pick up shared disaggregated metadata, serve reads, become leader, write/checkpoint, and repeat restart successfully.
