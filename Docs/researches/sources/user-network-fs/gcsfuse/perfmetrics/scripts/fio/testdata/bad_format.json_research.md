## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/bad_format.json

Purpose: Negative parser fixture for malformed FIO JSON.

APIs and structure: Starts with non-JSON text before an otherwise FIO-like object. It is consumed by `fio_metrics_test.test_load_file_dict_bad_format_file_raises_value_error`.

Control flow and state: No executable behavior. It exercises `json.load` failure in `_load_file_dict`.

Dependencies and risks: If the fixture is accidentally corrected into valid JSON, the malformed-file test stops proving parser rejection.

Test signals: Expected exception is `ValueError`.
