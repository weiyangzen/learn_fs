# File Research: sources/local-fs/mtd-utils/tests/fs-tests/run_all.sh

## Purpose
Top-level shell runner for the fs-tests suite.

## Key Elements
Chooses `$TEST_FILE_SYSTEM_MOUNT_DIR` or `/mnt/test_file_system`, clears it between tests, runs simple tests, `integrity/integck`, selected stress atoms, then `stress00.sh` and `stress01.sh` for 360 seconds each.

## Dependencies
Requires built test binaries, shell, `rm -rf`, and a safe mounted test directory.

## Behavior/Risks
Repeatedly executes `rm -rf ${TEST_DIR}/*` without quoting. A bad or empty test-dir configuration can be dangerous, though it defaults to `/mnt/test_file_system`.
