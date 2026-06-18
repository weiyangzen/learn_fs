# sources/storage-engines/foundationdb/contrib/joshua_logtool.py

## Purpose
`joshua_logtool.py` uploads and downloads FoundationDB simulation trace logs through the Joshua test cluster. It packages trace XML/JSON and optional app logs into an xz-compressed tar archive stored in a Joshua/FDB blob subspace keyed by ensemble ID and test UID.

## Important APIs, Types, And Functions
Constants define RocksDB trace event names and regexes for ensemble IDs and test UIDs. `console_log` prints status to stderr. `_execute_grep`, `_is_rocksdb_test`, `_extract_ensemble_id`, `_get_log_subspace`, `_tar_logs`, and `_tar_extract` provide helpers. `report_error(work_directory, log_directory, ensemble_id, test_uid)` implements upload. `download_logs(ensemble_id, test_uid)` reads and extracts an uploaded archive. `list_commands(ensemble_id)` prints download commands for tests found by `joshua.tail_results`. `_setup_args` creates subcommands `upload`, `download`, and `list`; `_main` opens Joshua and dispatches.

## Control Flow
Upload validates the log directory, finds `trace*.xml` and `trace*.json` recursively, optionally includes `app_log.txt` and `python_app_std*` when `TH_INCLUDE_APP_LOGS` is truthy, filters out filenames containing `core`, derives the ensemble ID from the argument or work-directory path, creates a temporary `.tar.xz`, uploads it via `joshua._insert_blob`, unlinks the archive, and reports success. Download creates a temporary file, reads a blob with `joshua._read_blob`, checks archive size, and extracts it into the current directory. List iterates Joshua results and extracts `TestUID` values from test harness output.

## State And Persistence Behavior
Persistent state is the compressed archive written into FoundationDB under `dir_ensemble_results_application/simulation_logs/<ensemble_id>/<test_uid>`. Temporary archives are created on local disk and normally removed after upload. Download writes extracted archive contents to the current working directory through `tar xf`. Logging and stderr console messages report progress.

## Dependencies And Integration Points
It depends on external `grep` and `tar`, the Python `fdb` bindings, and `joshua.joshua_model`. It integrates with Joshua ensemble result directories, FoundationDB subspaces, trace file naming conventions, and environment variable `TH_INCLUDE_APP_LOGS`.

## Risks And Edge Cases
`_is_rocksdb_test` is currently unused. `_tar_extract` extracts archives without target-directory isolation, so callers must trust archive contents and run from an intended directory. Temporary archive cleanup is skipped on some error returns before `unlink`. The ensemble regex expects work directories ending in `ensembles/<id>`. The upload path catches broad exceptions and returns without a nonzero code from `report_error`; `_main` exits nonzero only for exceptions escaping dispatch.

## Test Signals
Tests should mock Joshua blob APIs and subprocess calls to verify file discovery, core-file filtering, app-log inclusion, ensemble extraction, archive command formation, empty archive handling, download empty-blob behavior, and list command generation from harness output. Integration tests require a Joshua/FDB test database.
