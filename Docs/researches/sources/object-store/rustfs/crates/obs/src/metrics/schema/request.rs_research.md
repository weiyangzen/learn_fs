# sources/object-store/rustfs/crates/obs/src/metrics/schema/request.rs

## Purpose
Defines API request, rejection, latency distribution, and traffic descriptors.

## Important APIs, Types, and Functions
Exports label constants `NAME_LABEL`, `TYPE_LABEL`, and `LE_LABEL`. Rejection metrics are counters labeled by `type`. Waiting, incoming, and in-flight request metrics are gauges. Total, error, 4xx/5xx, canceled, TTFB distribution, sent bytes, and received bytes are counters. The TTFB distribution descriptor uses `name`, `type`, and `le`.

## Control Flow
Descriptors are lazily created using either `subsystems::API_REQUESTS` or `MetricSubsystem::ApiRequests`, which are equivalent.

## State and Persistence
No values here. Request collector code reads request stats and builds labeled Prometheus metrics, including histogram-bucket-like values for TTFB.

## Dependencies and Integration Points
Used by `metrics/collectors/request.rs`. The descriptor names come from `MetricName::Api*` variants. Full names compose under `rustfs_api_requests_*`.

## Risks
The TTFB distribution is built with `new_counter_md` rather than `new_histogram_md`; that may be intentional for bucket counters but can surprise consumers expecting histogram metadata. Label ordering and cardinality for `name` and `type` are critical. Several metrics split by API name can grow with endpoint variety.

## Test Signals
Request collector tests check representative names and labels. The entry-level histogram factory test does not cover this TTFB descriptor.
