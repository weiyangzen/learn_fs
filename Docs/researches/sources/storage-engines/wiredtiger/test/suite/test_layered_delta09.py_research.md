# sources/storage-engines/wiredtiger/test/suite/test_layered_delta09.py

Purpose: tests prefix and suffix compression interactions with page deltas. It ensures normal full-page compression stats behave as configured and that delta pages use expected prefix/suffix compression accounting while remaining readable on leader and follower.

Important APIs and functions: `test_layered_delta09` uses delta scenarios for leaf, internal, and both; `prefix_compression` table config; small page sizes; `stat.dsrc.rec_suffix_compression`, `rec_prefix_compression_full`, `rec_prefix_compression_delta`; `stat.conn.rec_page_delta_*`; and `stat.conn.cache_read_internal_delta`.

Control flow: `verify_compression` creates a table with or without prefix compression, inserts 1000 common-prefix keys, checkpoints, asserts full-page compression stats, reopens, updates a small key prefix range, checkpoints, checks delta stats, then verifies data after leader and follower reopens.

State and persistence behavior: common key prefixes create compression opportunities in base images and deltas. Reopens clear cache so both full image and delta compressed encodings must be decoded correctly. Follower mode validates the stored disaggregated representation.

Dependencies and integration: depends on page delta reconciliation, prefix/suffix compression counters, disaggregated reopen helpers, and internal delta read statistics. Risks include compression metadata mismatch between full images and deltas, delta reads failing when prefix compression is enabled, and stats changing under leaf/internal-only modes. Test signals are compression stat assertions plus complete key/value checks.
