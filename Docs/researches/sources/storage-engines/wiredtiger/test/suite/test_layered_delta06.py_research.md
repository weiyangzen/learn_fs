# sources/storage-engines/wiredtiger/test/suite/test_layered_delta06.py

Purpose: verifies that an empty or non-durable delta candidate is skipped and does not produce a leaf page delta, while stable data remains readable by a follower.

Important APIs and functions: `test_layered_delta06` uses compression/encryption scenarios, layered and file URI variants, `page_delta=(delta_pct=80)`, `precise_checkpoint=true`, `disaggregated=(lose_all_my_data=true)`, `local_files_action=ignore` in follower reopen, `stat.conn.rec_page_delta_leaf`, and timestamped reads.

Control flow: the test loads 100 rows at timestamp 5, sets stable timestamp and checkpoints, writes one later update at timestamp 10, checkpoints, then reopens as follower with complete checkpoint metadata. It reads at timestamp 5 and asserts all original values are present, then checks the leaf delta write statistic is zero.

State and persistence behavior: the later update is intentionally not part of the stable view being validated, so reconciliation should not persist an empty meaningful delta for the follower's stable read. `local_files_action=ignore` preserves needed local checkpoint metadata during reopen.

Dependencies and integration: depends on disaggregated storage metadata handling, page delta skip policy, timestamp visibility, compression/encryption extension loading, and follower reopen behavior. Risks include writing useless deltas, deleting local metadata before follower open, or exposing unstable updates. Test signals are stable timestamp value checks and `rec_page_delta_leaf == 0`.
