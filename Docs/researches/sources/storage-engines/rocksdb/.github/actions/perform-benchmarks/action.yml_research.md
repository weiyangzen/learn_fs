<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml

Purpose: Runs RocksDB low-variance benchmark CI with fixed environment settings.

Important APIs/types/functions: invokes `./tools/benchmark_ci.py` with `--db_dir`, `--output_dir`, and `--num_keys 20000000`. Sets benchmark env such as `DURATION_RO`, `DURATION_RW`, `NUM_THREADS`, `MAX_BACKGROUND_JOBS`, cache and compression options, and `CI_TESTS_ONLY=true`.

Control flow: after a release build, the benchmark script executes read/write benchmark scenarios and writes outputs under `${{ runner.temp }}/benchmark-results`.

State and persistence behavior: creates benchmark database data under runner temp and report files under benchmark-results. Persistence beyond the job is handled by `post-benchmarks`.

Dependencies and integration points: used by `benchmark-linux.yml` after `build-for-benchmarks`. Depends on built RocksDB binaries, Python benchmark tooling, and `LD_LIBRARY_PATH=/usr/local/lib`.

Risks: benchmark stability depends on runner isolation, disk performance, and temp storage capacity. Fixed large key counts and durations make it expensive. Environment variables are implicit contract with `benchmark_ci.py`.

Test signals: successful script exit and generated `report.tsv`/benchmark artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml -->
