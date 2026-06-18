# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable43.py

Purpose: multi-table RTS test covering dry-run, in-memory/disk modes, row/column formats, and worker counts 0 through 4. It ensures dry-run does not mutate and real RTS rolls many tables back consistently.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, repeated `large_updates` and `check` over ten tables, `session.checkpoint`, `conn.rollback_to_stable('dryrun=...,threads=N')`, and stats for calls, key removal/restoration, pages visited, and aborted updates.

Control flow: creates ten tables, pins oldest/stable to 1, writes values at 10/20/30/40, sets stable to 20, checkpoints disk cases, runs dry-run or real RTS, checks each table according to branch, then inspects stats.

State and persistence behavior: real RTS should remove updates after timestamp 20 across all tables; dry-run should leave the latest value visible. In-memory cases have different update-abort expectations because no disk checkpoint is used.

Dependencies and integration points: integrates multi-dhandle traversal, dry-run mode, in-memory configuration, and worker-thread fanout.

Risks: large scenario matrix can be expensive. Counter expectations differ significantly by dry-run and in-memory flags.

Test signals: per-table visibility checks and stats: one RTS call, no key removal/restoration, positive pages visited in disk cases, zero aborts in dry-run, and real-mode abort counts at least `nrows * 2 * ntables` where applicable.
