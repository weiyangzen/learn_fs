# sources/storage-engines/wiredtiger/test/suite/test_layered_delta07.py

Purpose: ensures durable entries are not redundantly included in new deltas, and that uncommitted or prepared updates cause reconciliation to skip page writes until they become durable. It covers normal updates, deletes, delete/update/restore, and prepared update/delete combinations.

Important APIs and functions: `test_layered_delta07` uses `page_delta=(delta_pct=100)`, `precise_checkpoint=true`, `preserve_prepared=true`, `stat.dsrc.rec_page_delta_leaf`, timestamp and oldest/stable timestamp advancement, prepared transaction APIs, explicit extra sessions, and debug eviction via `debug=(release_evict_page)`.

Control flow: each test loads ten rows, checkpoints stable base state, applies a durable update or delete and checkpoints to create a first delta. It then opens another session with uncommitted work and checkpoints again, asserting no new delta is written. Prepared tests checkpoint before and after commit/durable timestamp advancement and verify expected statistic increments.

State and persistence behavior: the file is mainly about reconciliation eligibility. Durable changes should appear once; uncommitted changes, prepared state, and already-durable deletes should not be reserialized into additional deltas. Oldest/stable timestamp changes are used to make deletes globally durable.

Dependencies and integration: depends on page delta reconciliation, timestamp/durable timestamp rules, prepared transaction preservation, data-source statistics, and eviction interaction. Risks include duplicate delta generation, including uncommitted updates in durable page state, or missing a committed prepared update. Test signals are exact `rec_page_delta_leaf` counts after each checkpoint.
