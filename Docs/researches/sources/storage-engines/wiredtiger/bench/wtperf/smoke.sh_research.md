# sources/storage-engines/wiredtiger/bench/wtperf/smoke.sh

## Purpose
`smoke.sh` provides a minimal manual/check smoke command for wtperf using the small-btree workload.

## Important APIs, Types, and Functions
It has no functions. It invokes `./wtperf -O \`dirname $0\`/runners/small-btree.wtperf -o "run_time=20"`.

## Control Flow
The script resolves the runner config relative to the script path and runs local `./wtperf` for 20 seconds. There is no `set -e`, but the final command exit status becomes the script exit status.

## State and Persistence Behavior
The invoked wtperf process creates its default WT home and output files such as `test.stat`, monitor data, and latency files depending on config defaults.

## Dependencies and Integration Points
It depends on the current directory containing `wtperf`, and the source/build layout containing `runners/small-btree.wtperf` relative to the script.

## Risks and Edge Cases
Running from a directory without `./wtperf` fails. Backtick command substitution and unquoted path can fail for paths with spaces. CMake's registered smoke variant is more robust than this script for build-tree execution.

## Test Signals
A successful zero exit after a 20-second small-btree run is the main signal. Confirm expected wtperf output files appear in the default home.
