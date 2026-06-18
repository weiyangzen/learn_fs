<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json

## Purpose
Peak received network bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/network/received_bytes_count`, metric kind `GAUGE`, and point values under `int64_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of peak received-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json -->
