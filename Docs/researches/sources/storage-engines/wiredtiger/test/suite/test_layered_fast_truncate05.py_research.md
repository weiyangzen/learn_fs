<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py

Purpose: tests that follower `next_random=true` cursors do not return keys hidden by a fast truncate range.

Important APIs/types/functions: `test_layered_fast_truncate05` uses the shared mixin setup/truncate helpers, zero-padded string keys, and a local `sample_assert_random` helper that opens `next_random=true` cursors and samples 200 keys inside a transaction.

Control flow: tests populate 1000 leader rows, reopen as follower, apply truncate 100-700, and repeatedly call `cursor.next()` on a random cursor. The second test first writes keys 200-400 into the follower ingest component, then truncates a range covering them and reuses the random-sampling assertion.

State and persistence behavior: the follower has a stable component from the checkpoint and optionally ingest updates. The truncate must hide both stable and ingest keys in the range when random selection traverses layered visibility.

Dependencies/integration points: depends on random cursor support over layered tables, disaggregated scenarios, and transaction-scoped cursor operations. Risks are probabilistic coverage because random sampling cannot prove absence exhaustively; the 200 draws are a regression signal, not a formal enumeration. Test signals are successful random cursor positioning and no sampled key between the truncated bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate05.py -->
