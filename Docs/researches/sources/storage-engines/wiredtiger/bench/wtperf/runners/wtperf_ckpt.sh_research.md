# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_ckpt.sh

## Purpose
`wtperf_ckpt.sh` automates wtperf checkpoint performance analysis. It can create/reuse a populated database, run checkpoint workloads, collect stack traces with `pmp`, and post-process result files into operation and checkpoint timelines.

## Important APIs, Types, and Functions
The script has option parsing for binary dir, root dir, optfile, debug/gdb, reuse, short run, verbose, and workload mode. Key variables are `WTPERF`, `DB_HOME`, `OUT_DIR`, `SHARED_OPTS`, `CREATE_OPTS`, and `RUN_OPTS`.

## Control Flow
It validates the wtperf binary, optionally creates a reusable database and tarball, creates a results directory, runs one checkpoint configuration, optionally samples `pmp` output every second while wtperf runs, copies `test.stat`, then extracts per-second read/insert/update lines and checkpoint on/off data using `get_ckpt.py`.

## State and Persistence Behavior
It deletes and recreates `WT_TEST`, `WT_TEST.tgz`, and `results`. It writes `.trace`, `.res`, `.out`, and `.ckpt` files. In reuse mode it restores database state from the tarball.

## Dependencies and Integration Points
It depends on local `wtperf`, `tar`, `pmp`, shell utilities, optional `gdb`, and companion `get_ckpt.py`. It assumes wtperf output format and `test.stat` naming.

## Risks and Edge Cases
The script is destructive to `WT_TEST` and `results` under `ROOT_DIR`. Some options concatenate without spaces (`-O$OPTARG`) and rely on wtperf parsing. `VERBOSE` is set to `0` even for `-v`, likely a bug. `pmp` may be unavailable. Result names are sanitized but still derived from option text.

## Test Signals
Run short mode (`-s`) against a built wtperf and verify `results` contains trace/res/out/ckpt artifacts. Reuse mode should avoid repopulation and still run workload successfully.
