<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh -->
# Research: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh

Purpose: Computes a round-robin subset of RocksDB test binaries for a CI shard.

Important APIs/types/functions: CLI `compute-test-shard.sh <shard_index> <num_shards>`; runs `make -s list_all_tests`, filters `_test` binaries, sorts them, forces `db_test` first, uses awk modulo assignment, writes `subset=...` to `GITHUB_OUTPUT`, and prints shard summary.

Control flow: generate total sorted list, reorder heavyweight `db_test`, select lines where `(NR - 1) % nshards == shard`, then expose the space-separated list.

State and persistence behavior: writes temporary files under `/tmp` and one GitHub step output; no repository changes.

Dependencies and integration points: intended for GitHub Actions jobs that build/run only `ROCKSDBTESTS_SUBSET`; depends on the Makefile's `list_all_tests` target.

Risks: no validation that shard index is within range or integer. Uses fixed `/tmp` filenames, so concurrent invocations in one runner could collide. Round-robin by sorted name is simple but not duration-aware.

Test signals: output summary with first/last/included counts and downstream shard jobs receiving the expected subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh -->
