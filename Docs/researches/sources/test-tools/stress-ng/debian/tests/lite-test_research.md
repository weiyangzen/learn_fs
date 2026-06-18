# sources/test-tools/stress-ng/debian/tests/lite-test

## Purpose
`debian/tests/lite-test` is a quicker autopkgtest smoke suite that runs a curated set of representative stressors for one second each.

## Important APIs, Types, And Functions
The script honors `STRESS_NG` or defaults to `stress-ng`, defines a fixed `STRESSORS` list including CPU, scheduler, data-structure, syscall, vector, and compression stressors, and runs `${STRESS_NG} -v -t 1 --${s} 4 --verify --timestamp` for each.

## Control Flow
It prints system information, iterates the fixed list, maps stress-ng exit codes to pass/fail/skip counters with the same convention as `fast-test-all`, records names, prints summary counts, and exits 1 only if a stressor returns code 2.

## State And Persistence
No intentional persistent state is created. Temporary files are managed by invoked stressors. Output is autopkgtest log text.

## Dependencies And Integration Points
It depends on shell, a runnable stress-ng binary, and stress-ng option/exit-code stability. The fixed list includes this subset's `af-alg` and many registry entries from `core-stressors.h`.

## Risks
The unquoted `[ -z $STRESS_NG ]` test is fragile. A fixed stressor list can lag renamed/removed stressors. Treating code 7 as a pass message but incrementing skipped count can make summary semantics confusing.

## Test Signals
A successful lite test has zero failures and reports pass/skip totals. It is a fast signal for broken binary startup, option parsing, and common stressor implementations.
