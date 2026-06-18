<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py

Purpose: regression test for WT-17267, ensuring `session.verify()` on a layered URI does not discard the follower's in-memory truncate list when it closes and reopens the layered dhandle.

Important APIs/types/functions: `test_layered_fast_truncate06` uses `LayeredFastTruncateConfigMixin`, `session.verify`, timestamped row inserts, `session.checkpoint`, and `super().setup_follower()` to reopen as follower. Scenarios cover both explicit `layered:` URI and table-layered form.

Control flow: `setup_follower` creates 100 integer-keyed rows on the leader, each with its own commit timestamp, checkpoints, and reopens as follower. The main test truncates 30-60, scans outside a transaction via `visible_keys_simple`, verifies the URI, and scans again.

State and persistence behavior: the tested state is the follower truncate list attached to the layered dhandle. It must survive dhandle lifecycle events induced by verify; otherwise truncated rows would reappear.

Dependencies/integration points: integrates verify with layered/disaggregated dhandle management and follower local truncate visibility. Risks are that verify behavior or dhandle cache policy changes can mask the original bug. Test signals are exact visible key lists before and after verify.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate06.py -->
