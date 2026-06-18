<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py

Purpose: Unit test suite for `vm_metrics.py`, using Monitoring response JSON fixtures to validate parsing, filter construction, error behavior, metadata handling, and metric conversion.

Important APIs, types, and functions: `MetricsResponseObject` and `dict_to_obj` convert fixture dictionaries into attribute-style objects. `create_metrics_value_by_type` builds `monitoring_v3.TypedValue` instances for bool, int64, double, string, and distribution values. `get_response_from_filename` loads `testdata/*.json` and constructs a `monitoring_v3.TimeSeries`. `TestVmmetricsTest` contains tests for `_get_instance_id`, `_parse_metric_value_by_type`, `_get_metric_filter`, `_validate_start_end_times`, and `_get_metrics` across CPU, memory, network, read bytes, latency, load average, and error count.

Control flow: Tests instantiate `VmMetrics` in `setUp`. API-facing tests patch `VmMetrics._get_api_response` to return either empty mappings or fixture-backed `TimeSeries` objects, then assert `MetricPoint` lists or exceptions. Metadata tests patch `subprocess.check_output` or `_get_instance_id`. The fixture builder manually maps JSON point intervals and values to protobuf objects because TimeSeries JSON is not deserialized directly.

State and persistence behavior: Reads fixture files under `./testdata`; does not write persistent state. It patches process execution and Monitoring calls, so tests do not require live GCP. Some expected constants mirror production metric descriptors but include a memory metric type (`agent.googleapis.com/memory/percent_used`) that differs from the production `agent.googleapis.com/processes/rss_usage`, making test coverage partly historical.

Dependencies and integration points: Depends on `unittest`, `mock`/`unittest.mock`, `google.cloud.monitoring_v3`, `google.api.distribution_pb2`, fixture JSON, and the local `vm_metrics` module. It exercises the same Monitoring value-type codes as production.

Risks and test signals: Strong signals include empty response behavior for every metric class, distribution mean parsing, int64/double conversion, agent/custom/compute filter strings, and synthesized zero error-count series. Gaps include no direct test for `fetch_metrics` row zipping, no Google Sheets write assertion, no unsupported `test_type` handling, and limited coverage of `_get_gcsfuse_pid` shell parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/vm_metrics_test.py -->
