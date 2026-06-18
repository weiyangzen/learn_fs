# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress01.sh

## Purpose
Smaller concurrent stress workload script.

## Key Elements
Computes free space, sets workload size to one-fifteenth of free space, and runs `fstest_monitor` with four `fwrite00` variants and one `rndwrite00`, optionally duration-limited.

## Dependencies
Requires `free_space`, `fstest_monitor`, atom binaries, and configured test mount.

## Behavior/Risks
Destructive concurrent fill/write/unlink workload. Final cleanup uses unquoted `${TEST_DIR}/*`.
