## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_metrics.json

Purpose: Negative FIO fixture for valid JSON with no usable nonzero metrics.

APIs and structure: Contains FIO-like global and job sections, but the selected read metrics are zeroed such that the parser skips the job and ends with no extracted jobs.

Control flow and state: No executable behavior.

Dependencies and risks: It must keep required keys present, otherwise it would trigger missing-key errors instead of the no-data path.

Test signals: `_extract_metrics` should raise `NoValuesError('No data could be extracted from file')`.
