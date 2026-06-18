# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size03.py

Purpose: regression suite for disaggregated checkpoint-size leaks involving `bytes_total`, page deltas, full-page rewrites, eviction, and cumulative-size reconstruction.

Important APIs and control flow: configured as disaggregated leader with page deltas enabled. `get_checkpoint_size` reads latest stable metadata size. Tests rewrite constant-size data under different `page_delta` settings, inspect `stat.dsrc.rec_page_delta_leaf`, evict pages with `debug=(release_evict)`, force full images by reconfiguring `delta_pct=1`, and compare final sizes to baselines.

State and persistence: state lives in disaggregated stable page images, delta chains, and metadata size fields. Eviction forces pages to be read back from page service to exercise cumulative-size restoration.

Dependencies and integration: uses `DisaggConfigMixin`, page-delta configuration, dsrc stats, metadata cursors, transactions, and debug eviction.

Risks and test signals: size must remain near baseline despite repeated rewrites. Failures indicate leaked old blocks, incorrect delta chain termination, or cumulative-size mis-accounting after eviction.
