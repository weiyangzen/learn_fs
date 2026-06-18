# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.cpp

Purpose: Implements collection and JSON output of performance metrics.

Important APIs/types/functions: `metrics_writer::instance` returns a process singleton. `output_perf_file` writes `<test_name>.json` containing one object with `info.test_name` and a metrics array. The templated `add_stat` implementation is in the header.

Control flow: metrics are appended during monitor finish; output is generated on demand and trims the trailing comma if metrics exist.

State and persistence: `_stats` holds JSON fragments in memory; output persists to a JSON file in the current working directory.

Dependencies/integration: used by `metrics_monitor` for saved stats and likely top-level test runners for final output.

Risks and test signals: metric names are not JSON-escaped beyond simple string concatenation, so unusual names could produce invalid JSON. An empty metric list still produces a valid empty array.
