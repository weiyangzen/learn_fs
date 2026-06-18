# sources/user-network-fs/samba/source4/torture/tests/test_locktest.sh

## Purpose
`test_locktest.sh` is a blackbox wrapper for the `locktest` executable. It runs deterministic locking behavior tests against two server shares and reports success or failure through Samba's subunit shell harness.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It locates `locktest` under `$BINDIR`, optionally prefixes the command with `$VALGRIND`, and uses `testit` from `../../../testprogs/blackbox/subunit.sh`.

## Control Flow
The script validates the argument count, assigns positional variables, shifts the first five arguments, initializes `failed=0`, and calls `testit "locktest"` with `//$SERVER/test1`, `//$SERVER/test2`, `--num-ops=100`, domain, and `--user1="$DOMAIN\\$USERNAME%$PASSWORD"`. Any additional arguments are appended. The script exits with the accumulated failure count.

## State and Persistence Behavior
The wrapper itself writes no files despite accepting `PREFIX`. Remote test state is created by `locktest` on the two test shares, including lock and file operation state that the executable is responsible for cleaning up.

## Dependencies and Integration Points
It depends on a built `locktest` binary, two configured test shares, valid domain credentials, optional Valgrind integration, and the blackbox subunit helper.

## Risks
The script assumes both test shares exist and are safe for destructive locking tests. Because it passes only `user1`, coverage is tied to the default behavior of `locktest` for the second side. Any quoting or domain-format mismatch can prevent authentication.

## Test Signals
A zero exit indicates the lock operation sequence completed as expected. Nonzero exit reports either command setup failure or locktest-detected locking divergence.
