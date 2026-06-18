## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/constants.py

Purpose: Central constants for FIO JSON parsing and unit conversion.

APIs and data: Defines JSON key names for global/job options, params, read/write metrics, latency percentile keys, and conversion tables `FILESIZE_TO_KB_CONVERSION` and `TIME_TO_MS_CONVERSION`. `NS_TO_S` converts nanoseconds to seconds.

Control flow and state: No functions or mutable runtime state. Constants are imported by `fio_metrics.py` and tests.

Dependencies and risks: File-size conversion uses decimal KB multiples for M/G/T/P rather than binary. `_convert_value` lowercases units before lookup, so table keys are lower-case.

Test signals: Indirectly covered by `fio_metrics_test` conversion, parameter, and metric extraction tests.
