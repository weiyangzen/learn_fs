# sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTest.sh

Purpose: Joshua wrapper for extended-duration simulation correctness runs. It disables ASAN leak detection, validates `JOSHUA_SEED`, creates a `th_longrunning_*` temp directory, and invokes TestHarness2 with `--long-running`.

Important APIs and control flow: uses `JOSHUA_SEED`, `OLDBINDIR`, `TH_OUTPUT_DIR`, and `DIAG_LOG_DIR`. It calls `python3 -m test_harness.app --joshua-seed ... --old-binaries-path ... --long-running --run-temp-dir ...`, redirecting Python stderr into the run directory.

State and persistence: run artifacts persist in the created temp directory; there is no cleanup trap in this wrapper, so lifecycle is owned by TestHarness2 config or external Joshua cleanup.

Dependencies and integration: depends on TestHarness2 and old binary path convention. `--long-running` maps to `run.py` disabling simulation speedup and using no timeout.

Risks and test signals: no stdout tee/fallback XML guard compared with `correctnessTest.sh`, so early Python failure can produce poor Joshua output. Test signals include long-running command line knobs in trace/config and absence of external timeout.
