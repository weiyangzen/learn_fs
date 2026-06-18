<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py

Purpose: verifies follower truncate composition with existing truncates, per-key removes, and reinsertion.

Important APIs/types/functions: uses the shared mixin plus local `remove_key`, which opens a cursor, positions on `self.key(key)`, and calls `cursor.remove()` in a transaction. Scenarios cover both URI forms.

Control flow: each test builds a 1-100 follower dataset, then performs combinations: per-key remove before truncate, same truncate twice, broader truncate after a narrower one, overlapping ranges, disjoint ranges, bounded plus open-ended ranges, truncate then reinsert within the same transaction, and truncate then reinsert in a later transaction.

State and persistence behavior: multiple truncate-list entries must compose as unions for scans; duplicate entries must be harmless. Per-key tombstones and later inserted values must layer correctly over earlier range tombstones. Reinsertion at key 45 is expected to make only that key visible within the formerly truncated range.

Dependencies/integration points: stresses update-chain ordering in the ingest component, range-list overlap logic, and transaction-local ordering when truncate and insert occur in one transaction. Risks include redundant truncates corrupting state or reinserts being masked. Test signals are exact expected visible-key lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate13.py -->
