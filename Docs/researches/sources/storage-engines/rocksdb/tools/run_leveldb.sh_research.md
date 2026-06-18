# sources/storage-engines/rocksdb/tools/run_leveldb.sh

## Purpose
This Bash script runs a LevelDB-compatible benchmark sequence using `tools/benchmark_leveldb.sh`. It is intended for comparing RocksDB and a specific LevelDB fork, with setup writes followed by read-only and read-write workloads.

## Important APIs, Types, and Functions
The script is top-level Bash and uses environment tunables `NKEYS`, `NWRITESPERSEC`, `VAL_SIZE`, `BLOCK_LENGTH`, `CACHE_BYTES`, `DATA_DIR`, `DO_SETUP`, and `SAVE_SETUP`. It builds `ARGS` and calls `./tools/benchmark_leveldb.sh` for `fillseq`, `overwrite`, `readrandom`, and `readwhilewriting`.

## Control Flow
It parses optional thread-count arguments or defaults to 24. Setup mode creates the DB through large-value fillseq, normal fillseq, and single-threaded overwrite. Restore mode copies `${DATA_DIR}.bak` into place. Optional save mode refreshes the backup. It then loops over thread counts for random reads and overwrite/readwhilewriting tests, and builds `report2.txt` from `report.txt` with grep filters.

## State and Persistence
It writes output to `${TMPDIR:-/tmp}/output`, creates/removes `DATA_DIR`, and can create or restore `${DATA_DIR}.bak`. There is no WAL-dir handling because LevelDB benchmark settings differ from RocksDB.

## Dependencies and Integration Points
It depends on `tools/benchmark_leveldb.sh`, shell utilities, and the modified LevelDB benchmark interface described in the comments. It is operationally parallel to `run_flash_bench.sh` but for LevelDB.

## Risks
It lacks strict shell failure handling and uses `rm -rf` on environment-derived paths. Summary greps include tests that are commented out, so some sections may be empty. The header comment references `run_flash_bench.sh`, likely copied text. Defaults are large and can produce expensive runs.

## Test Signals
Successful completion produces `report.txt`, `report2.txt`, and per-test logs under the output directory. The reports are the comparison signal.
