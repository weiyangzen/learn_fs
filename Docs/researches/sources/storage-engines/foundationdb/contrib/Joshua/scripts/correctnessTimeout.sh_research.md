# sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTimeout.sh

Purpose: timeout-side Joshua wrapper for normal correctness tests. It converts a scheduler timeout into TestHarness2 summaries by running `python3 -m test_harness.timeout`.

Important APIs and control flow: no custom functions or arguments. The script uses `bash -u`, so unset variable expansions would fail, but it does not read shell variables directly. It delegates all behavior to `test_harness.timeout`, which scans the current working tree for trace files and emits killed-test summaries.

State and persistence: it does not create state itself. It assumes the current directory contains run artifacts from an interrupted TestHarness2/fdbserver execution.

Dependencies and integration: depends on Python module import path and the timeout module. It is paired with `correctnessTest.sh` in Joshua job configuration.

Risks and test signals: no explicit error handling; import failures or no traces mean Python behavior determines output. Test by running in a temp directory with trace files and verifying an `ExternalTimeout` summary is emitted.
