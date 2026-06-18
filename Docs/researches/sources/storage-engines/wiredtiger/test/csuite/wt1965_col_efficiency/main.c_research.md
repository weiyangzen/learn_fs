# sources/storage-engines/wiredtiger/test/csuite/wt1965_col_efficiency/main.c

Purpose: this workload demonstrates the WT-1965 column-store inefficiency involving sparse record IDs. It is primarily a performance/efficiency regression test rather than a correctness oracle.

Important APIs, types, and functions: it uses `WT_SESSION`, `WT_CURSOR`, pthreads, column-store `key_format=r`, fixed-width `Q` value fields, a secondary `table:index`, and common test options. `thread_func` is the workload function. It uses an atomic fetch-add on `opts->next_threadid` to assign thread indexes and a global timestamp counter `g_ts`.

Control flow: `main` opens a 1GB-cache logged database with eviction/checkpoint tuning, builds a value format containing eight `Q` fields, creates the primary sparse recno table and an index table, starts four threads, joins them, then scans the primary table. Each thread inserts records whose recnos are `ins_thr_idx << 40 | ins_rotor`, creating huge key gaps. Each insert also writes an index row keyed by object id and timestamp, then mutates two fields in its per-object data array and sleeps to approximate 5K updates/sec.

State and persistence behavior: the test persists sparse recno records and index records in a temporary home. It does not crash or recover. The value state is a timestamp plus eight counters per object, where counters change gradually between insert rotations.

Dependencies and integration points: it relies on WiredTiger handling very sparse column-store record numbers efficiently enough to finish. Verbose mode prints decoded records for inspection.

Risks and test signals: there is no explicit performance threshold, so failure is usually timeout, excessive CPU, assertion, or API error. The global `g_ts` is incremented without synchronization beyond the workload's loose benchmarking intent, so it should not be treated as a strict correctness timestamp source.
