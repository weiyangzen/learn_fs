# sources/test-tools/fio/t/random_seed.py

Purpose: regression tests for fio random seed semantics. It ensures `randseed` overrides repeat settings, repeat-enabled runs are deterministic, and repeat-disabled runs produce different seeds unless an explicit seed is supplied.

Important APIs and types: `FioRandTest` extends `FioJobCmdTest`, runs the null ioengine with `--debug=random`, and extracts `rand_seeds[]` from output. `TestRR` keeps class-level seed lists for `[all]randrepeat` values 0 and 1. `TestRS` keeps a class-level dictionary keyed by explicit `randseed`.

Control flow: `main()` parses common run controls, creates an artifact directory, resolves fio, builds a 17-case test list, and calls `run_fio_tests()`. Each case captures debug output. `TestRR.check_result()` stores the first seed sequence for a repeat mode and compares later runs for expected equality or inequality. `TestRS.check_result()` does the same per explicit seed and also compares against other explicit seeds.

State and persistence: class variables persist seed baselines across test cases in the same process. Artifacts include fio output files under the run directory. The tests use null I/O and do not modify external storage.

Dependencies and integration points: depends on fio debug output format, Python 3, fiotestlib, and the umbrella runner. `run-fio-tests.py` registers this as executable test 1013.

Risks and test signals: parsing is fragile if debug line wording changes, and `get_rand_seeds()` silently proceeds if `FIO_RAND_NR_OFFS` is not found. The central success signal is matching or non-matching seed arrays according to repeat and explicit seed rules, plus the underlying fio process success.
