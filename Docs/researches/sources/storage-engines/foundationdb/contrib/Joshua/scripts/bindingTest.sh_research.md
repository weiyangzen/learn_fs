# sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTest.sh

## Purpose
Joshua entrypoint for the legacy binding tester package.

## Important APIs, Types, and Functions
Sets script directory, enables core dumps, unsets external client directory, creates a per-process temp work directory, and invokes `bindingTestScript.sh 1` with test environment variables.

## Control Flow and Integration
Joshua copies this as `joshua_test`; when run from a package directory it prepares isolation and delegates all cluster/test work to the main script.

## State and Persistence
Depends on sibling `bindingTestScript.sh` and package layout with binaries/scripts in the working directory.

## Dependencies
Runtime state is `tmp/$$` under the current directory, core dump settings, and environment variables.

## Risks and Test Signals
Risks include temp directory collisions only guarded by PID and inherited environment leakage except for one unset variable. Test signal is one successful binding tester cycle.
