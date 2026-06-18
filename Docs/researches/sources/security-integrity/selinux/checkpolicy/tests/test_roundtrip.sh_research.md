# sources/security-integrity/selinux/checkpolicy/tests/test_roundtrip.sh

## Purpose

`test_roundtrip.sh` is the shell test harness for checkpolicy source-to-binary-to-source round trips. It validates that selected policy fixtures compile, decompile into canonical source, and remain idempotent when the canonical output is compiled and decompiled again.

## Important Functions And Flow

The script uses `set -eu`, computes `BASEDIR=$(dirname "$0")`, and sets `CHECKPOLICY="${BASEDIR}/../checkpolicy"`. The `check_policy()` function takes `POLICY`, `EXPECTED`, and `OPTS`. It compiles `${POLICY}` into `testpol.bin`, decompiles that binary with `-b -F` into `testpol.conf`, diffs against `${EXPECTED}`, then repeats the compile/decompile cycle using `${EXPECTED}` as input to ensure expected files are stable canonical forms.

The harness runs minimal non-MLS, minimal MLS, allonce non-MLS, allonce MLS, and allonce Xen lanes with option combinations covering `-E`, `-M`, `-S -O`, `--target xen`, and `-c 30`.

## State And Persistence

The script writes transient `testpol.bin` and `testpol.conf` into the tests directory and overwrites them on each lane. It does not clean them at the end. Exit state is controlled by shell `set -e` and `diff` return codes.

## Dependencies And Integration Points

It depends on the sibling `checkpolicy` binary, POSIX shell, `diff`, and the fixture/expected files in the same directory. It is an integration point for parser, optimizer, binary serializer, and source decompiler behavior.

## Risks

Because transient files are written in the source tests directory, concurrent test runs can race or produce confusing diffs. `BASEDIR=$(dirname "$0")` is robust for relative invocation but does not canonicalize symlinks. The script assumes `checkpolicy` is built at the expected path.

## Test Signals

A successful run means every fixture compiles, decompiles, matches expected canonical text, and the expected canonical text is idempotent. The lane names printed before each test make it straightforward to isolate which fixture or option set failed.
