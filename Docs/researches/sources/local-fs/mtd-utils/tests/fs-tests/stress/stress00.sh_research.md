# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress00.sh

## Purpose
Concurrent stress workload script combining many atom tests.

## Key Elements
Computes free space for the test mount, sets each file workload to one-fifteenth of free space, then runs `fstest_monitor` with many `fwrite00` variants, `rndwrite00`, and `pdfrun`, optionally bounded by a duration argument.

## Dependencies
Requires `../utils/free_space`, `../utils/fstest_monitor`, built atom binaries, shell arithmetic, and a mounted test directory.

## Behavior/Risks
Runs many destructive workloads concurrently and clears `${TEST_DIR}/*` at the end without quoting.
