# sources/storage-engines/wiredtiger/tools/pytest_parallel

Purpose: runs selected WiredTiger Python suite tests in parallel from a build directory while labeling output and preserving per-test WT home directories.

Important APIs and control flow: shell functions `Usage()`, `waitone()`, `showprocs()`, and `label_output()` handle help, error attribution, progress diagnostics, and output prefixing. Argument parsing accepts `-j`, `--python`, `--help`, arbitrary `run.py` options before `--`, and test filenames after `--`. It requires a local `wt` executable, deletes `WT_TEST.*`, then starts `../test/suite/run.py -D WT_TEST.<test> --noremove ...` jobs up to the parallel limit. `waitone()` uses `wait -n`, compares job lists before/after, records failed process names, and exits nonzero if any failed.

State and persistence behavior: deletes `WT_TEST.*` in the build directory, creates per-test `WT_TEST.<pyfile>` homes, and may create TSAN log directories when `TESTUTIL_TSAN=1`. It mutates `TSAN_OPTIONS` while launching tests and restores it afterward.

Dependencies and integration points: depends on Bash job control, associative arrays, `nproc`, `sed`, `git rev-parse` for TSAN log paths, Python, and WiredTiger `test/suite/run.py`. It is a faster alternative to `run.py -j` for independent test scripts.

Risks: deleting `WT_TEST.*` is broad. `waitone()` can misattribute failures if multiple jobs exit between before/after snapshots. Test names are used in directory and log path construction. It must run from a build directory, not the source root.

Test signals: success prints `Success`; failures print labeled output and a summary. Useful validation is running a small pair of known passing tests with `-j 2`.
