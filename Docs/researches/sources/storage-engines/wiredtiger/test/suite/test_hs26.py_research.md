# sources/storage-engines/wiredtiger/test/suite/test_hs26.py

Purpose: tests variable-length column-store history-store reads when RLE groups from older and newer batches overlap. It targets corruption/loss risks when duplicate values are reconciled, RLE-encoded, evicted, and later read through history.

Important APIs and functions: `test_hs26` uses `SimpleDataSet` with `key_format='r'` and `value_format='S'`. Scenario axes cover whether the first timestamp is globally visible, first/second row counts (`103` or `211`), and RLE grouping moduli (`7`, `13`, `17`). Helpers `make_value`, `make_updates`, `expected_value`, `expected_numvalues`, and `check` encapsulate the generated value pattern and read validation.

Control flow: the test populates an empty table, pins oldest/stable to 1, writes the first duplicate-value run at timestamp 2, optionally advances oldest/stable to make it globally visible, opens a long-running read transaction at timestamp 2, writes a second run at timestamp 100, verifies reads at both timestamps, evicts every 41st key via `debug=(release_evict)`, then validates the old reader and latest reader again.

State and persistence behavior: old versions remain visible through a pinned timestamp reader while newer versions may force older values into the history store. The RLE suffix pattern makes adjacent values compressible while mismatched group sizes create overlap at group boundaries.

Dependencies and integration points: depends on `wtdataset.SimpleDataSet`, `wtscenario.make_scenarios`, timestamp visibility, history-store reads, and variable-length column-store RLE reconciliation.

Risks and edge cases: important risks are off-by-one RLE grouping errors, incorrect key counts when the second write has fewer rows, and failure to retain old values after eviction. It is deliberately column-store-only because the hazard is tied to VLCS RLE encoding.

Test signals: `check` asserts exact value content and expected record counts before and after eviction for timestamp 2 and timestamp 100.
