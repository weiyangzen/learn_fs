<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py

Purpose: long-running randomized stress test for follower fast truncate correctness across repeated leader/follower switches in disaggregated WiredTiger.

Important APIs/types/functions: defines `operations` enum, `OpenTruncate`, `HistoryEntry`, `ValidationModel`, and `test_layered_fast_truncate_stress01`. It uses `random`, timestamped transactions, `disagg_switch_follower_and_leader`, `disagg_advance_checkpoint`, and model-based validation.

Control flow: `populate_initial_leader` seeds all keys and the validation model. Each round builds a random stream of inserts, updates, removes, and truncates; keeps non-overlapping truncates open; commits them at new timestamps; skips conflicting single-key writes inside open truncate ranges; then switches roles, restarts the old leader as follower, advances checkpoint, and validates the new leader. Regular mode uses 5000 keys and 160 rounds; long mode scales to 200000 keys and 1600 rounds.

State and persistence behavior: `ValidationModel` stores full per-key timestamp history, latest snapshots, and value-at-timestamp lookups. It verifies both current full scans and sampled historical reads after every switch.

Dependencies/integration points: integrates randomized workload generation, role switching, checkpoint pickup, follower truncate replay, and MVCC history. Risks include deliberate exclusion of write-conflict scenarios (FIXME-WT-17637) and seed-dependent failures. Test signals include reproducible seed logging, full-scan equality, and sampled point-read assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate_stress01.py -->
