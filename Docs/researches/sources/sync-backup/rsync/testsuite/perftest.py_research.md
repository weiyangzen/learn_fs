## sources/sync-backup/rsync/testsuite/perftest.py

Purpose: standalone developer benchmark for comparing transfer performance of two local rsync binaries over deterministic generated or existing trees.

Important APIs and types: `Binary` dataclass records label, path, and version. Tree generation uses `parse_size()`, `human()`, `gen_sizes()`, `build_dirs()`, `write_file()`, `rel_symlink()`, `safe_rmtree()`, and `generate_tree()`. Benchmarking uses `rsync_version()`, `drop_caches()`, `time_transfer()`, `run_benchmark()`, `_stats()`, `report()`, `_write_csv()`, and `main()`.

Control flow: CLI validates two executable binaries and run count, creates or uses a workdir, generates a heavy-tailed tree unless `--src` is provided, pre-populates a no-op destination, alternates binary order each loop, optionally drops caches, times full and/or no-op transfers, drops warmups from statistics, reports mean/stddev/min/median and regression/faster/no-change verdicts, optionally writes raw CSV, and cleans scratch unless `--keep`.

State and dependencies: creates scratch source/dest trees marked by `.perftest`, may write CSV, and may write `/proc/sys/vm/drop_caches` as root.

Integration points: not part of `runtests.py`; it evaluates real binary performance for archive/hard-link default args and generated symlinks/hardlinks/modes.

Risks and test signals: benchmark noise, caching, storage performance, and non-fsync behavior affect interpretation. Signals are repeated timing samples and threshold comparison against run-to-run stddev.
