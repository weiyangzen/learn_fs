# sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/smoke.sh

## Purpose
This smoke wrapper runs WT-4105 in row-store and column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves test binary from an optional argument or `$binary_dir/test_wt4105_large_doc_small_upd`.
- Uses `$TEST_WRAPPER` for harness integration.

## Control Flow
After binary resolution, it invokes the binary with `-t r` and `-t c`.

## State and Persistence Behavior
No direct script state; the binary creates its WiredTiger home and large table.

## Dependencies and Integration Points
Assumes CMake copies the script next to the binary or that the binary path is passed manually.

## Risks and Test Signals
Either row or column mode failure exits the script. Manual execution outside the build tree needs an explicit binary path or `binary_dir`.
