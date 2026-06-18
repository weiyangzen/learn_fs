# sources/object-store/openstack-swift/swift/common/middleware/x_profile/profile_model.py

## Purpose
`profile_model.py` provides the data model for xprofile output. `Stats2` extends `pstats.Stats` with JSON, CSV, and ODS serializers, while `ProfileLog` manages profile dump discovery, selection, atomic dump writes, and deletion. Together they are the persistence and serialization layer consumed by `HTMLViewer` and `ProfileMiddleware`.

## Important APIs, types, and functions
`Stats2` preserves the `pstats.Stats` API and adds `func_to_dict()`, `func_std_string()`, `to_json()`, `to_csv()`, and `to_ods()`. `to_json()` includes summary fields, selected functions, callees, callers, and timing metrics. `to_csv()` writes a simple CRLF-separated profile table. `to_ods()` creates an OpenDocument spreadsheet through optional `odfpy`. `ProfileLog(log_filename_prefix, dump_timestamp)` exposes `get_all_pids()`, `get_logfiles(id_or_name)`, `dump_profile(profiler, pid)`, and `clear(id_or_name)`.

## Control flow and state behavior
`Stats2` loads profile files through its `pstats.Stats` superclass. Each serializer starts from either the sorted function list or all stats keys, applies selection arguments with `eval_print_amount()`, then walks `self.stats`. `to_json()` calls `calc_callees()` and serializes nested caller/callee metrics, accommodating eventlet metrics that may be a tuple or a scalar. `ProfileLog` treats profile files as names beginning with `log_filename_prefix`; timestamped dumps use `PREFIX + pid + "-" + time.time()`. Dumps are written to `.tmp` first via `profiler.dump_stats()` and then renamed into place.

`get_logfiles('all')` returns either every non-temp profile file or, when `dump_timestamp` is true, the latest file per process id according to reverse-sorted profile ID strings. `current` maps to `os.getpid()`. `clear()` deletes the selected files if they exist.

## Dependencies and integration points
Dependencies include `glob`, `json`, `os`, `pstats`, `tempfile`, `time`, and optional `odfpy`. `HTMLViewer` constructs `Stats2` to render pages and exports. `ProfileMiddleware.dump_checkpoint()` calls `ProfileLog.dump_profile()` asynchronously from a green pool; `ProfileMiddleware.__del__()` and clear actions call `ProfileLog.clear()`.

## Risks and edge cases
The profile file selection logic assumes names after the prefix split cleanly into `process_id-timestamp`; malformed names can break `get_logfiles('all')` when timestamp mode is enabled. Reverse string sorting of timestamps generally works for decimal epoch strings but is not as explicit as numeric sorting. Profile files are trusted input to `pstats.Stats`, so corrupt files raise load failures upstream. `to_csv()` performs manual CSV construction without quoting function names. `to_ods()` depends on optional `odfpy` and writes values with mixed numeric/string types. Clear operations unlink whatever files match the prefix and selected profile id.

## Test signals
Tests should exercise non-timestamped and timestamped profile discovery, current/all/specific id selection, `.tmp` exclusion, atomic dump rename behavior, clear semantics, JSON caller/callee output for tuple and scalar metrics, CSV formatting, ODS dependency failure, and serializer selection filtering.
