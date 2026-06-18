# sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/smoke.sh

## Purpose
This smoke wrapper runs WT-6616 checkpoint/oldest timestamp recovery testing in row and column modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves optional binary argument or `$binary_dir/test_wt6616_checkpoint_oldest_ts`.
- Uses `$TEST_WRAPPER`.

## Control Flow
The script runs the binary once with default row-store behavior and once with `-c` for column-store mode.

## State and Persistence Behavior
The script itself is stateless. The binary creates a child process, sentinel file, recovered database, and optional debug copy.

## Dependencies and Integration Points
It assumes build-tree placement or explicit binary path, and is part of csuite smoke coverage.

## Risks and Test Signals
Any failure in either mode stops the script. The binary has randomized duration unless overridden, so smoke runtime can vary.
