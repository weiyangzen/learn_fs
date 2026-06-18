<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py

Purpose: validates follower cursor read paths over fast-truncated ranges, including scans, `search`, `search_near`, open-ended bounds, multiple ranges, overlaps, appends, and updated-then-truncated keys.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin` methods `setup_leader`, `setup_follower`, `truncate`, `visible_keys`, `search_near_key`, `populate`, and `key_exists`. The local `key` returns zero-padded string keys so string ordering matches numeric ordering; scenarios cover both `layered:` and table-layered URIs.

Control flow: each test populates 1000 leader rows, reopens as follower, applies one or more truncates, and then checks expected key lists. Cases cover bounded [100,700], full-table truncates, truncates to end, disjoint and overlapping ranges, mixed bounded/open-ended ranges, appends after open-ended truncate, local updates later covered by truncate, and `search_near` direction fallback.

State and persistence behavior: open-ended truncates capture the end key at commit time rather than hiding later appends; follower ingest updates remain visible only if not later covered by truncate.

Dependencies/integration points: exercises logical layering between stable and ingest tables and layered cursor positioning. Risks are off-by-one boundary bugs and direction-specific cursor leaks. Test signals are exact visible-key arrays, boolean key existence, and `search_near` landed keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate04.py -->
