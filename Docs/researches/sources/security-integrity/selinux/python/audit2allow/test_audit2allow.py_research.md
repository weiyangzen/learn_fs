<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py -->
# sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py

## Purpose
Provides unit/integration tests for the audit2allow toolchain using local scripts and a dummy binary policy.

## Important APIs, Types, And Functions
Defines `Audit2allowTests(unittest.TestCase)` with assertion helpers `assertDenied`, `assertNotFound`, `assertFailure`, `assertSuccess`, and test methods `test_sepolgen_ifgen`, `test_audit2allow`, `test_audit2why`, and `test_xperms`. It uses `mkdtemp`, `Popen`, `PIPE`, `sys.executable`, and local files `test_dummy_policy` and `test.log`.

## Control Flow
Each test spawns a command in the current source directory. `test_sepolgen_ifgen` writes interface info to a temporary directory with the local helper and deletes it. `test_audit2allow` and `test_audit2why` run the local scripts with the dummy policy and log. `test_xperms` verifies generated output contains `allowxperm`.

## State And Persistence
Creates and removes a temporary directory/output file. Other tests are read-only aside from subprocess output.

## Dependencies And Integration Points
Runs under the audit2allow Makefile after building `test_dummy_policy` and the helper. It assumes source-directory relative paths.

## Risks And Edge Cases
The tests capture only stdout, so stderr diagnostics are not inspected despite variables named `err`. Temporary cleanup lacks `finally`, so failures can leave directories.

## Test Signals
Passing tests indicate the helper, audit2allow, audit2why, xperm path, dummy policy, and fixture log are minimally functional.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py -->
