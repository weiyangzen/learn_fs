# sources/test-tools/fio/t/run-fio-tests.py

Purpose: umbrella test launcher for fio's Python/job-file/executable regression tests. It centralizes the test manifest, environment construction, requirement checking, artifact directory setup, pass-through arguments, and final failure exit code.

Important APIs and types: specialized `FioJobFileTest_*` classes extend `FioJobFileTest` for job-specific assertions around JSON totals, latency fields, offset logs, trimwrite pairing, log file formats, pattern files, and random offset distribution. It imports `FioExeTest`, `FioJobFileTest`, `run_fio_tests`, and all `fiotestcommon` requirement and success constants. `TEST_LIST` maps numeric IDs to job files or executables with expected status and requirements.

Control flow: custom classes override `check_result()` or `setup()` to inspect artifacts after the base class validates fio execution. `main()` parses root, fio path, artifacts, skip/run-only, requirement bypass, pass-through arguments, NVMe character device, cleanup, and debug settings. It resolves `fio_root` and `fio_path`, warns if fio is missing, creates `fio-test-*`, optionally initializes `Requirements`, builds `test_env`, and delegates execution to `run_fio_tests()`.

State and persistence: artifacts are created under a timestamped root and may be cleaned for passing tests when requested through the shared library. Some tests generate pattern files or parse per-job logs in test directories. The manifest itself is static, but pass-through arguments are stored in `test_env`.

Dependencies and integration points: depends on Python, statsmodels runs test, fiotestlib, fiotestcommon, platform-specific requirements, job files under `t/`, compiled helper binaries, optional CUnit, zbd/null_blk support, libaio, io_uring, NVMe character devices, and multiple executable Python harnesses. It is the primary integration point tying many files in this subset into fio CI-style execution.

Risks and test signals: several checks have tolerance bands or statistical assumptions and can be workload or host sensitive. The manifest includes destructive NVMe tests only behind requirements and an explicit `--nvmecdev`. Success signals include base execution status, specialized JSON/log assertions, requirement skip accounting, and process exit equal to the failed test count.
