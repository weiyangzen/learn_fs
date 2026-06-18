<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_search_near02.py

Purpose: timestamped variant of search-near past end, ensuring an invisible last-key update or delete does not hide the older visible value.

Important APIs/types/functions: `test_search_near02` mirrors `test_search_near01` with scenarios for record-number and row keys, update/delete mode, checkpoint, release eviction, commit timestamps, and read timestamps.

Control flow: insert keys 1 through 1000 with value 1, checkpoint and evict them, update or delete key 1000 at commit timestamp 10, then open a transaction at read timestamp 5 and call `search_near` for key 1100.

State and persistence behavior: the committed change at ts 10 is not visible to the read at ts 5, so both update and delete scenarios must position on key 1000 with value 1. This validates history/update-chain visibility at the high end of the key space after eviction.

Dependencies/integration points: integrates cursor positioning, timestamp visibility, tombstones, row/VLCS formats, and on-disk pages. Risks mirror the non-timestamped test plus timestamp setup assumptions; signals are exact key 1000 and old value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near02.py -->
