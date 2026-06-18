## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/missing_metric_key.json

Purpose: Negative FIO fixture for missing required metric keys.

APIs and structure: FIO-like JSON with a job whose metric tree lacks at least one nested key required by `REQ_JOB_METRICS`. It is loaded successfully but fails during `_extract_metrics`.

Control flow and state: No executable behavior.

Dependencies and risks: The fixture must remain valid JSON while omitting the target metric; otherwise it would exercise the wrong parser failure.

Test signals: `fio_metrics_test` expects `NoValuesError` matching `Required metric .* not present in json output`.
