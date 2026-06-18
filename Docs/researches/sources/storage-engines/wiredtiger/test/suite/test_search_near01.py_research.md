<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_search_near01.py

Purpose: verifies `search_near` behavior for a search key past the end of a table after the last key is updated or deleted.

Important APIs/types/functions: `test_search_near01` uses scenarios for record-number and row-store integer keys, update/delete modes, table creation, cursor operations, checkpoint, and `debug=(release_evict)`.

Control flow: create a file object with integer values, insert keys 1 through 1000 with value 1, checkpoint, evict all rows, then either delete key 1000 or update it to value 2. Start a transaction, set the cursor key to 1100, call `search_near`, and verify the positioned key/value.

State and persistence behavior: checkpoint and eviction force a disk image with later in-memory changes to the last key. Delete mode expects the nearest visible key to move to 999; update mode expects key 1000 with the new value.

Dependencies/integration points: covers cursor search-near positioning, row-store and VLCS key spaces, deletion visibility, and eviction. Risks include implicit transaction visibility and not checking the return sign from `search_near`; signals are exact positioned key/value assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_search_near01.py -->
