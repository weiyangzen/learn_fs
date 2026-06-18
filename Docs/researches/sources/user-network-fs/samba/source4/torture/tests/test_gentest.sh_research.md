# sources/user-network-fs/samba/source4/torture/tests/test_gentest.sh

## Purpose
`test_gentest.sh` is a blackbox wrapper for the `gentest` differential SMB operation generator. It runs `gentest` against two test shares on the same server using deterministic seeds and reports the outcome through Samba's subunit shell helpers.

## Important APIs, Types, and Functions
The script expects `SERVER USERNAME PASSWORD DOMAIN PREFIX` plus optional extra arguments. It uses environment variable `BINDIR` to locate `gentest`, optional `VALGRIND`, and sources `../../../testprogs/blackbox/subunit.sh` for `testit`. It creates `$PREFIX/gentest.ignore` containing fields to ignore: `all_info.out.fname` and `internal_information.out.file_id`.

## Control Flow
After validating the argument count, the script assigns positional arguments, shifts them away, initializes `failed=0`, writes the ignore file, and invokes `testit "gentest"` with `//$SERVER/test1` and `//$SERVER/test2`, `--seed=1`, `--seedsfile=$PREFIX/gentest_seeds.dat`, `--num-ops=100`, the ignore file, domain, and two identical user credentials. It increments `failed` if `testit` fails, removes the ignore file, and exits with the failure count.

## State and Persistence Behavior
The wrapper creates a temporary ignore file and a persistent seed file under `PREFIX`. The remote side is mutated by `gentest` under its own test paths on the `test1` and `test2` shares. The script removes only the ignore file.

## Dependencies and Integration Points
It integrates the standalone `gentest` executable into Samba's blackbox test harness and depends on configured shares `test1` and `test2`, credentials, `BINDIR`, and subunit shell reporting.

## Risks
The test is destructive to the remote test shares. The same username/password is used for both user roles, which is intentional for this wrapper but limits multi-user coverage. Missing `PREFIX`, missing `BINDIR`, or absent test shares result in setup failures.

## Test Signals
The subunit `testit` result is the primary signal. A zero exit means `gentest` completed 100 deterministic operations without unignored divergence; nonzero means the differential generator or setup failed.
