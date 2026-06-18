# sources/storage-engines/wiredtiger/test/suite/test_layered_delta14.py

Purpose: tests that reconciliation skips writing full pages when it does not make progress, with leaf page deltas disabled and precise checkpointing enabled.

Important APIs and functions: `test_layered_delta14` uses a layered table, `page_delta=(leaf_page_delta=false)`, `precise_checkpoint=true`, `checkpoint_and_verify_stats`, `wiredtiger.stat.dsrc.rec_page_full_image_leaf`, timestamped writes, and the disaggregated leader role.

Control flow: the test creates a layered table, inserts data, advances timestamps, and performs checkpoints while verifying full-page image statistics. It drives a case where reconciliation should recognize no progress and avoid unnecessary full-page writes.

State and persistence behavior: with leaf deltas disabled, reconciliation might otherwise fall back to full images. The intended behavior is to skip page writes when the durable page image would not advance useful state. Timestamps define which writes are eligible for checkpoint materialization.

Dependencies and integration: depends on layered disaggregated reconciliation, precise checkpoint accounting, page delta configuration, and WiredTiger test helper `checkpoint_and_verify_stats`. Risks include excessive full-page writes, checkpoint churn, or stats failing to distinguish skipped pages. Test signals are the expected full-image leaf statistic values observed through the helper.
