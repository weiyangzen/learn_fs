# sources/storage-engines/rocksdb/build_tools/check_progress.sh research

Purpose: `check_progress.sh` emits a JSON progress summary for RocksDB builds/tests. It is designed for machine polling while tests are being generated, compiled, linked, or executed.

Important APIs: the command takes no arguments and writes one JSON object to stdout. Helper functions are `json_escape()`, `output_json()`, and `get_failed_tests_json()`. Output fields include `status`, optional `phase`, `completed`, `total`, `failed`, `percent`, `eta_seconds`, `avg_time`, `last_item`, and optional `failed_tests`.

Control flow: if `LOG` exists, the script treats the run as test execution. It counts generated `t/run-*` files, completed rows in `LOG`, failures by exit/signal columns, failed-test logs from `t/log-run-*`, percentage, last test, average runtime, ETA, and status. Without `LOG`, it estimates compile/link progress from `src.mk`, object files in known source directories, and executable `*_test` binaries. If no artifacts exist, it reports `not_started`.

State and persistence: it reads build artifacts but does not write them. It shells out to Python 3 for robust JSON escaping when available, otherwise uses sed/awk fallback escaping. Failed test output is capped at 50 lines and 10 failures.

Dependencies and integration: it depends on Bash, coreutils, find, awk, sed, optional Python 3, the RocksDB parallel test `LOG` format, `t/` test scripts, and `src.mk`.

Risks and test signals: JSON correctness depends on escape fallback quality and unescaped numeric assumptions for exit/signal values. Compile progress is heuristic and tied to a hardcoded directory list. `find -printf` is GNU-specific. Tests should simulate LOG rows, failed logs, missing logs, generation phase, compile artifacts, and environments without Python 3.
