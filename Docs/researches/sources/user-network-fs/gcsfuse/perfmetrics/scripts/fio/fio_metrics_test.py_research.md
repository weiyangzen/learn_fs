## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics_test.py

Purpose: Unit test suite for FIO metrics parsing.

APIs and control flow: Uses `unittest` with fixture filenames in `./fio/testdata/`. Tests cover `_load_file_dict` success and error modes, `_convert_value`, `_get_rw`, job parameter extraction, start/end time error behavior, global and job ramp time handling, `_extract_metrics`, skipped zero-metric jobs, `NoValuesError` paths, `get_metrics`, and multiple job scenarios with global or job-level options.

State and persistence: Reads JSON fixtures from the testdata folder. Does not touch Google Sheets or BigQuery.

Dependencies and risks: Tests assume they are run from `perfmetrics/scripts` because `TEST_PATH` is relative. Expected dict order mirrors the parser's insertion order.

Test signals: Strong parser coverage, but no CLI-main or upload integration coverage.
