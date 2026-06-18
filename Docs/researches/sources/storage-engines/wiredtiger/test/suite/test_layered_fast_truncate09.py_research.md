<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py

Purpose: covers transaction and timestamp visibility rules for follower truncate-list entries.

Important APIs/types/functions: `test_layered_fast_truncate09` uses `wiredtiger.WT_NOTFOUND`, explicit sessions, `with self.transaction(...)`, local `truncate_range`, `search_in`, `search_near_in`, `next_key_after`, and `commit_truncate`. It sets up in `setUp`, so each test starts with a populated follower.

Control flow: setup writes 1000 integer-keyed stable rows at timestamp 10, checkpoints at stable timestamp 10, and reopens as follower. Tests assert a session sees its own uncommitted truncate, another session ignores that uncommitted truncate, rollback restores visibility, committed truncates obey read timestamps, and overlapping truncates at timestamps 20 and 40 expose only the timestamp-visible delete ranges.

State and persistence behavior: truncate entries participate in transaction isolation and timestamp visibility, including overlap union only for entries visible to the reader.

Dependencies/integration points: integrates session isolation, read timestamps, layered `search`, `search_near`, and cursor `next` movement. Risks include helper methods opening cursors outside caller transaction expectations. Test signals are search return/value tuples, `search_near` exact/landed pairs, and next-key assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate09.py -->
