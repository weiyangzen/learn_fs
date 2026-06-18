# sources/user-network-fs/rclone/fs/rc/rcserver/metrics_test.go

## Purpose
This file tests the Prometheus metrics endpoint exposed by the RC metrics server.

## Important APIs, Types, and Functions
- `testMetricsServer` creates a metrics server and reuses `emulateCalls` from RC server tests.
- `newMetricsTestOpt` enables metrics listening on the test bind address.
- `TestMetrics` asserts baseline metrics, mutates global accounting stats, and asserts changed metrics.
- `makeMetricsTestCases` builds regex expectations for byte, check, error, delete, and transfer counters.

## Control Flow
The test installs a config file environment, constructs the server without binding a real external port, calls the chi router with synthetic HTTP requests, and checks status/body regexes.

## State and Persistence
It mutates `accounting.GlobalStats`, so it relies on test isolation and may be sensitive to other tests changing global stats in the same process. No disk persistence is intentional beyond config setup.

## Dependencies and Integration Points
It imports the local backend for filesystem availability, `configfile.Install`, `accounting`, `rc.Options`, and the `testRun` harness from `rcserver_test.go`.

## Risks and Edge Cases
Because metrics are global, test ordering or parallel execution with other accounting tests could change expected values. The tests assert selected metric lines rather than full Prometheus output.

## Test Signals
The file provides direct evidence that the metrics route returns HTTP 200 and exposes current accounting counters in Prometheus text format.
