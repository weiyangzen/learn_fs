## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics.py

Purpose: Parses FIO JSON output into rows suitable for Google Sheets and BigQuery.

APIs and control flow: Dataclasses `JobParam` and `JobMetric` describe required parameter and metric extraction. Helpers `_convert_value` and `_get_rw` normalize units and read/write modes. `FioMetrics` loads JSON, reads global/job ramp times, derives start/end windows, merges global job params with job overrides, extracts required metrics from read/write sections, skips jobs with invalid time windows or all-zero metrics, formats upload rows, and exposes `get_metrics(filepath)`.

State and persistence: Reads only the input JSON file. Upload imports are present but this module's main path prints parsed metrics rather than uploading.

Dependencies and risks: Assumes every job has `job options` when iterating params and that global params exist if job options omit a required param. Missing nested metrics raise `NoValuesError`. `_convert_value` handles integers only and can fail on decimal sizes/times. Dict insertion order controls upload column order.

Test signals: Extensive unit tests cover load failures, conversion failures, rw normalization, ramp time, good/partial/missing/no-data, and multiple-job global/job-option cases.
