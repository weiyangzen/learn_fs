# sources/storage-engines/wiredtiger/tools/backup_analysis.py

## Purpose
`backup_analysis.py` compares two WiredTiger backup directories and reports how many bytes and incremental-backup granularity blocks changed between them. It classifies files into MongoDB-oriented categories to summarize replication, oplog, local, and system table change patterns.

## Important APIs and functions
Core functions include `get_metadata`, `get_checkpoint_time`, `older_dir`, `compute_type`, `check_backup`, `compare_file`, `print_summary`, `compare_backups`, and `backup_analysis`. `TypeStats` accumulates per-category bytes, changed blocks, file counts, changed-file counts, granularity-block counts, small-change counts, large-change counts, and single-block-file counts.

## Control flow and behavior
The script validates two distinct backup directories containing `WiredTiger.backup`, determines which is older from `WiredTigerHS.wt` checkpoint metadata, compares `.wt` and `.wti` files common to both directories, and reports files created/dropped between backups. `compare_file` reads common file prefixes in 4096-byte chunks, rolls differences into caller-specified granularity blocks, prints verbose or terse per-file output, and updates global type statistics. `print_summary` aggregates totals and per-type percentages.

## State, dependencies, and integration
State is held in module globals `compare_size`, `pct20`, `pct80`, and `typestats`. The script depends on backup metadata format, MongoDB naming conventions (`collection`, `index`, oplog metadata), POSIX file paths, Python stdlib modules, and readable backup data files. It is a diagnostic command-line tool, not part of WiredTiger runtime.

## Risks and test signals
Risks include brittle metadata parsing, assertions instead of graceful errors for missing metadata or type mismatches, division by zero for unusual empty inputs, only overlapping bytes being compared, and integer-only granularity. Signals are per-file change reports, created/dropped file messages, summary percentages, correct category classification, and exit after `backup_analysis(opts)` with status `0`.
