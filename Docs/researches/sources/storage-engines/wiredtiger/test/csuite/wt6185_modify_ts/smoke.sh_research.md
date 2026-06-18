# sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/smoke.sh

## Purpose
This smoke wrapper runs WT-6185 timestamped modify testing in row-store and variable-length column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves an optional binary argument or defaults to `$binary_dir/test_wt6185_modify_ts`.
- Uses `$TEST_WRAPPER`.

## Control Flow
The script invokes the binary once with default row-store behavior and once with `-C` for column-store mode.

## State and Persistence Behavior
The script creates no direct state. The binary creates timestamped WiredTiger files and removes them unless preserved.

## Dependencies and Integration Points
Assumes CMake-copied script location or explicit binary path. It maps csuite smoke coverage to both key formats.

## Risks and Test Signals
Any binary failure stops the script. Without extra options, checkpoint and eviction remain enabled in both modes.
