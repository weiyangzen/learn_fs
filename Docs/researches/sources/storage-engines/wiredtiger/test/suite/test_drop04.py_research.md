# sources/storage-engines/wiredtiger/test/suite/test_drop04.py

Purpose: regression test for WT-15225, repeatedly creating and dropping an empty logged table after checkpoint cleanup.

Important APIs and control flow: `test_drop04` extends `test_cc_base`, enabling checkpoint cleanup coordination. With logging enabled, `test_drop_after_bulk_load` loops 100 times: create `table:test_drop04`, wait for checkpoint cleanup using `wait_for_cc_to_run`, then drop with `force=false`.

State and persistence: the table is empty but logged. The test stresses metadata, logging, and checkpoint cleanup interactions rather than data content.

Dependencies and integration: imports `test_cc_base`, uses `wttest`, logging config, and checkpoint cleanup helpers.

Risks and test signals: repeated success is the signal. Failures would expose races or stale metadata state when dropping recently created empty logged tables after checkpoint cleanup.
