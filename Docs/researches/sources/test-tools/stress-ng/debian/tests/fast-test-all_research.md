# sources/test-tools/stress-ng/debian/tests/fast-test-all

## Purpose
`debian/tests/fast-test-all` is an autopkgtest script that runs every built-in stressor briefly, excluding a small known-risk set, and summarizes pass/fail/skip counts.

## Important APIs, Types, And Functions
The script honors `STRESS_NG` or defaults to `stress-ng`, obtains stressor names with `--stressors`, defines `not_exclude`, and loops through stressors. Each included stressor runs as `${STRESS_NG} -v -t 1 --${s} 4 --verify --timestamp --metrics --vmstat 1`.

## Control Flow
The script prints system information, iterates discovered stressors, skips names in `EXCLUDE` (`l1cache` currently), runs each stressor, maps stress-ng exit codes 0 through 7 to pass/skip/fail categories, records names, and exits 1 if any stressor returns failure code 2.

## State And Persistence
It does not create intentional persistent files. Stressors under test may create temporary files or system effects according to their own cleanup. Output is the autopkgtest log.

## Dependencies And Integration Points
It depends on a runnable stress-ng binary in PATH or `STRESS_NG`, shell utilities, and stress-ng exit-code conventions. It directly exercises `core-stressors.h` registry output and reporting paths such as `core-vmstat.c`.

## Risks
Running every stressor can be noisy and environment-sensitive even with one-second duration. The unquoted `[ -z $STRESS_NG ]` test can misbehave when the variable contains whitespace or shell metacharacters. The script treats many abnormal returns as skipped, so only code 2 fails the test.

## Test Signals
Autopkgtest pass requires zero code-2 failures. Logs list passed, failed, and skipped stressor names, making registry or stressor-specific regressions visible.
