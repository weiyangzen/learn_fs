<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py

Purpose: comprehensively validates cursor iteration and point-search APIs over follower truncated ranges.

Important APIs/types/functions: uses shared helpers `visible_keys`, `key_exists`, `search_near_key`, `populate`, `auto_closing_cursor`, `transaction`, `concat`, and `range_inclusive`. The local `random_sample_keys` reads from a `next_random=true` cursor.

Control flow: tests create followers with keys 1-100 or stable-only setup, truncate ranges such as 30-60 or 30-end, and verify forward scans, backward scans, random cursor samples, search inside/boundary cases, `search_near` inside/boundary cases, forward-then-backward fallback, and choosing a live ingest key inside an earlier truncated stable range before the next stable key.

State and persistence behavior: truncates hide stable keys, but later follower ingest writes can make a key in the range visible again at the latest view. API paths must converge on the same logical visibility.

Dependencies/integration points: exercises multiple cursor implementations in the layered cursor. Risks include random sample probabilism and direction-sensitive cursor bugs. Test signals are exact scan lists, no random key in range, boolean searches, and expected `search_near` exact/landed pairs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate12.py -->
