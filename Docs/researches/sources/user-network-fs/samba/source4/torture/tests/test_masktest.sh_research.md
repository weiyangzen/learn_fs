# sources/user-network-fs/samba/source4/torture/tests/test_masktest.sh

## Purpose
`test_masktest.sh` is a blackbox wrapper for Samba's `masktest` executable. It exercises wildcard and filename mask behavior against a temporary SMB share path and emits the result through subunit.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It resolves `masktest` from `$BINDIR`, supports `$VALGRIND`, and sources the standard blackbox `subunit.sh` to use `testit`.

## Control Flow
After argument validation, the script initializes variables and calls `testit "masktest"` with `//$SERVER/tmp`, `--num-ops=200`, `--dieonerror`, domain, and `-U"$USERNAME%$PASSWORD"`, followed by any extra arguments. Failures increment `failed`; the script exits with that value.

## State and Persistence Behavior
The wrapper writes no local files and does not use `PREFIX`. The `masktest` binary mutates the remote `tmp` share while generating and checking mask operations and is responsible for cleanup.

## Dependencies and Integration Points
It integrates `masktest` into the Samba blackbox suite and requires a built binary, a writable `tmp` share, credentials, and the blackbox subunit helper.

## Risks
The remote `tmp` share must be disposable. `--dieonerror` makes the test stop on the first detected mismatch, which is useful for CI but may reduce evidence from later generated operations. Authentication format differs from `test_locktest.sh` because it omits the domain prefix in `-U`.

## Test Signals
A zero exit indicates 200 mask operations completed without mismatch. Nonzero exit indicates a wrapper setup problem or masktest-detected wildcard/mask behavior failure.
