# sources/storage-engines/wiredtiger/test/suite/test_layered_delta08.py

Purpose: validates internal page deltas that record deleted child/leaf page references after large delete ranges in a disaggregated file table.

Important APIs and functions: `test_layered_delta08` uses small page sizes, `block_manager=disagg`, `page_delta=(internal_page_delta=true,leaf_page_delta=false)`, `stat.dsrc.rec_page_delta_internal_key_deleted`, `stat.dsrc.rec_page_delta_internal`, helpers `insert`, `delete_keys`, `verify`, and timestamped range verification.

Control flow: the test inserts 5000 rows, checkpoints, reopens to force disk state, deletes two large disjoint key ranges at later timestamps, advances oldest and stable timestamps before each checkpoint, and then verifies internal deleted-key delta stats. It checks the latest visible key set before and after reopening.

State and persistence behavior: the two delete ranges remove enough rows to affect multiple leaves and internal keys. Internal reconciliation should encode deleted child keys in deltas, and reopening should apply those deltas to reconstruct the tree with only expected keys present.

Dependencies and integration: integrates internal page delta encoding, deleted-child metadata, timestamped delete visibility, disaggregated file tables, and statistics. Risks include orphaned internal references, deleted keys remaining visible, internal delta not being written when leaf deltas are disabled, and reopen reconstruction failures. Test signals are statistic thresholds and per-key search/`WT_NOTFOUND` validation at the stable timestamp.
