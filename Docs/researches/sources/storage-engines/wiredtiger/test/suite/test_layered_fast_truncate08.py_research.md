<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py

Purpose: ensures follower range truncate writes the layered tombstone sentinel into the ingest file instead of creating normal `WT_UPDATE_TOMBSTONE` records via `cursor->remove()`.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `contextlib.closing`, byte-string value format `value_format=u`, local `populate`, `get_values`, and direct inspection of `file:<test_name>.wt_ingest`.

Control flow: the leader creates the initial layered table and checkpoint through `setup_layered_table`; the follower reopens and populates ingest keys 0-99. The test truncates 20-80, opens the ingest file directly, and searches every key in the range to collect stored values.

State and persistence behavior: follower truncate is represented as real ingest rows carrying sentinel value `b"\x14\x14"`, so direct ingest-file search still finds each truncated key. This differentiates layered tombstone encoding from ordinary delete tombstones that would be invisible to a cursor search.

Dependencies/integration points: tightly coupled to ingest file naming (`.wt_ingest`) and sentinel encoding. Risks are false failures if sentinel representation or ingest filename convention changes. Test signals are value count equal to truncated key count and all values matching the sentinel.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate08.py -->
