<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config04.py

Purpose: individually tests connection-level configuration options and parser edge cases.

Important APIs and control flow: helper methods open with `create,statistics=(fast)`, populate a table, read statistics, or check log-file placement. Tests cover cache size suffixes and min/max bounds, eviction percentage and absolute-size validation, dirty/update/checkpoint target ordering, unknown keys, malformed brackets/quotes/escapes, quoted valid configs, error prefixes, log paths, multiprocess, session max, default transactional behavior, and still-accepted removed LSM metadata options.

State, persistence, and dependencies: successful tests create tables and sometimes log files in default, relative, or absolute directories. Dependencies include `wiredtiger`, `wttest`, `stat.conn.cache_bytes_max`, filesystem directories, and optional hook awareness for tiered/disagg error-message matching.

Integration points: broad coverage of the public connection configuration grammar and semantic validation logic.

Risks and test signals: many assertions match error text and can be affected by hook-added configs. Removed LSM config acceptance is an upgrade compatibility signal. Failures usually reveal config parser, validation, stats, or log path regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config04.py -->
