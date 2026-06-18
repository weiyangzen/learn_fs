<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py

Purpose: checks that `cursor.next()` skips truncated stable keys after `search_near` lands exactly on an ingest key.

Important APIs/types/functions: class `test_layered_fast_truncate14` uses `LayeredFastTruncateConfigMixin` and local `keys_after_search_near`, which positions a cursor with `search_near`, requires exact match, then drains subsequent `next()` keys inside a rollback transaction.

Control flow: tests set up small stable key sets and follower ingest keys, truncate a range in stable space, call `keys_after_search_near` from an ingest key, and assert the subsequent sequence omits any truncated stable key. Cases include one truncated stable key, multiple consecutive stable keys, an ingest key adjacent to the range, and multiple ingest keys before the truncated gap.

State and persistence behavior: the cursor is positioned on ingest while the next stable candidate may be hidden by the truncate list. The layered cursor must advance past hidden stable keys and continue merging remaining stable/ingest keys.

Dependencies/integration points: narrow integration test for layered merge-cursor movement after `search_near`. Risks are stateful cursor-position bugs that only appear after exact ingest hits. Test signals are absence of truncated keys and exact next-key lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate14.py -->
