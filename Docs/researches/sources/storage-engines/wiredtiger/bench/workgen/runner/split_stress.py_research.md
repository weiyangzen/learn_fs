<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py

Purpose: stresses page split paths and split races with small cache, small pages, fast split deepening, and concurrent random-order inserts.

Important APIs and functions: uses `op_multi_table`, insert operations, Workgen thread multiplication, table range settings, and latency output.

Control flow: open a 100 MB cache connection with statistics logging; create three file tables with 8 KB leaf/internal pages, key/value max 1433, memory page max 1 MB, and `split_deepen_min_child=100`; populate 50,000 rows across tables; run 20 insert threads across all tables for 300 seconds.

State and persistence: creates three file tables and grows them through concurrent inserts. Writes `latency.out`.

Dependencies and integration: split stress benchmark for WiredTiger btree concurrency.

Risks: small cache and aggressive split config are intentionally stressful and can expose races. Operation distribution depends on Workgen range/key behavior.

Test signals: populate/workload assertions, latency output, statistics log, and absence of split failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py -->
