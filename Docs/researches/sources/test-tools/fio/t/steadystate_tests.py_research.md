# sources/test-tools/fio/t/steadystate_tests.py

Purpose: direct functional and parser tests for fio steady-state detection. It verifies parse-time debug messages for `--ss` options and runtime JSON steady-state fields for null-engine read workloads.

Important APIs and functions: `check()` recalculates either slope or maximum deviation over fio's steady-state data for IOPS or bandwidth, in absolute or percent terms, using SciPy linear regression for slope mode. The main block performs all parsing and workload tests without fiotestlib classes.

Control flow: after parsing a fio executable path, it runs parse-only commands and searches debug output for expected strings. It then defines several read workload scenarios, invokes fio with JSON output files, loads each JSON file, and for every reported job checks attained/not-attained state, minimum runtime versus ramp/duration, criterion equality, and threshold comparison. It prints per-job pass/fail lines and exits with the failure count.

State and persistence: writes `steadystate_jobN.json` files in the current directory and leaves them behind. It has no external storage side effects because it uses the null ioengine.

Dependencies and integration points: requires Python with SciPy, fio JSON output, and subprocess access. It is invoked by `run-fio-tests.py` as executable test 1004.

Risks and test signals: comments acknowledge limited coverage: option parsing and read tests only. Runtime tolerance and steady-state behavior can be sensitive to timing, though null engine reduces variance. Success signals are matching parser messages, JSON criterion recalculation, correct runtime behavior, and final zero failure exit.
