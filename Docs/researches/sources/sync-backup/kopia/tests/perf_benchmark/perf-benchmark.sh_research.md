
# sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark.sh

## Purpose
Runs Kopia performance benchmark scenarios for a specified package version/channel and total source size, collecting `psrecord` CPU/RAM logs and repository size logs.

## Important APIs, Types, And Functions
Shell variables `VERSION`, `CHANNEL`, `TOTAL_SIZE`, and `fio_opts` configure the run. The script installs Kopia from the Kopia APT repository, then loops over compressed/uncompressed scenarios with 10/100/1000 files.

## Control Flow
For each scenario, it clears `/mnt/data/{repo,cache,source}`, creates a repo, generates test files with `fio`, optionally enables `s2-default` compression, records an initial snapshot with `psrecord`, clears cache, reconnects, records a second snapshot, and writes `du -bs` repository size output.

## State And Persistence Behavior
Mutates system APT sources, installs/downgrades Kopia, repeatedly removes benchmark data under `/mnt/data`, creates repository/cache/source trees, and writes `psrecord-...log` and `repo-size-...log` files in the current directory.

## Dependencies And Integration Points
Depends on `curl`, `apt-key`, `apt`, `fio`, `psrecord`, `sudo`, `/mnt/data`, and Kopia CLI package repositories.

## Risks And Edge Cases
The cache clear lines use `/mnt/data/cache}` with an extra `}`, likely clearing/creating the wrong path and leaving `/mnt/data/cache` intact. That can invalidate second-run cold-cache measurements. The script assumes APT repository availability and has broad destructive `rm -rfv` operations under `/mnt/data`.

## Test Signals
Produces benchmark logs for throughput/resource comparison rather than pass/fail tests. Output is consumed by `process_results.go`.
