# sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/smoke.sh

## Purpose
This smoke wrapper runs the WT-2909 checkpoint integrity executable in both row-store and column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Parses optional `-b <builddir>` and forwards it as `-b` to the test binary for extension discovery.
- Uses `TEST_WRAPPER` if set by the harness.

## Control Flow
The script resolves the test binary either from its first non-option argument or from `$binary_dir/test_wt2909_checkpoint_integrity`, where `binary_dir` defaults to the script directory. It invokes the binary twice: once with `-t r` and once with `-t c`.

## State and Persistence Behavior
The script itself creates no state. The invoked test creates and removes WiredTiger homes and may create child stdout/stderr files.

## Dependencies and Integration Points
It is copied into the build tree by CMake csuite definitions and assumes `TEST_WRAPPER` may prefix execution. The `-b` option is essential when the fail filesystem extension is not discoverable relative to the copied script.

## Risks and Test Signals
Any failing row or column run exits the script due to `set -e`. Manual execution outside the build directory must pass the binary path or set `binary_dir`.
