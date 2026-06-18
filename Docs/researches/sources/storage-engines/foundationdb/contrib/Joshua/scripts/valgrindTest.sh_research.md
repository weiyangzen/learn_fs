# sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTest.sh

Purpose: Joshua wrapper for running simulation correctness tests under Valgrind. It validates `JOSHUA_SEED`, creates `th_valgrind_*`, and invokes TestHarness2 with `--use-valgrind`.

Important APIs and control flow: consumes `JOSHUA_SEED`, `OLDBINDIR`, `TH_OUTPUT_DIR`, and `DIAG_LOG_DIR`; passes `--old-binaries-path`, `--use-valgrind`, and `--run-temp-dir` to `test_harness.app`.

State and persistence: artifacts and Valgrind XML are written under the run temp directory. Cleanup behavior is mostly delegated to TestHarness2.

Dependencies and integration: requires `valgrind` available to `run.py`, TestHarness2, current `fdbserver`, and optional debug path env. In `run.py`, only the current binary is valgrinded, not old restart binaries.

Risks and test signals: lacks the richer fallback/capture logic of `correctnessTest.sh`. Test signals include generated `valgrind-<seed>.xml`, `ValgrindError` summary children for non-leak errors, and longer timeout multiplier.
