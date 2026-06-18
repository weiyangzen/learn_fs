<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py

## Purpose
Fetches VM metric summaries for a supplied time range and writes them to the `ml_metrics` Google Sheet tab.

## Important APIs, Types, And Functions
CLI takes `<start_time> <end_time>`, computes period, and calls `VmMetrics.fetch_metrics_and_write_to_google_sheet` with operation `read`.

## Control Flow
Validates argument count, waits 250 seconds for Cloud Monitoring samples, constructs a `VmMetrics` client, parses epoch boundaries, derives period, and delegates fetch/upload.

## State And Persistence Behavior
Sleeps, performs Cloud Monitoring reads, and writes Google Sheet output through the VM metrics helper.

## Dependencies
Uses `socket.gethostname`, `time`, and `vm_metrics.vm_metrics`; `populate_metrics.sh` installs requirements and fetches credentials.

## Integration Points
Paired with `populate_metrics.sh` and used for ML model metric backfill.

## Risks And Edge Cases
Fixed wait time, no validation that end is after start, and unused `metric_data_name` constant suggests older output contracts.

## Test Signals
No direct tests in this subset; VM metrics JSON fixtures support the underlying helper tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py -->
