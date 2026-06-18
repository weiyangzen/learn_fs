# sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket.rs

Purpose: defines bucket API metric descriptors for bucket-scoped traffic, request counts, error counts, cancellation counts, in-flight requests, and TTFB distribution.

Important APIs/types: descriptors include `BUCKET_API_TRAFFIC_SENT_BYTES_MD`, `BUCKET_API_TRAFFIC_RECV_BYTES_MD`, `BUCKET_API_REQUESTS_IN_FLIGHT_MD`, `BUCKET_API_REQUESTS_TOTAL_MD`, `BUCKET_API_REQUESTS_CANCELED_MD`, `BUCKET_API_REQUESTS_4XX_ERRORS_MD`, `BUCKET_API_REQUESTS_5XX_ERRORS_MD`, and `BUCKET_API_REQUESTS_TTFB_SECONDS_DISTRIBUTION_MD`.

Control flow: each descriptor is lazily built using `new_counter_md`, `new_gauge_md`, or `new_histogram_md` with `subsystems::BUCKET_API`. Labels include combinations of `bucket`, `name`, `type`, and histogram `le`.

State/persistence: lazy descriptor initialization only.

Dependencies/integration: used by the bucket API collector outside this work item and by any request/bucket reporting path that wants bucket-scoped API metrics.

Risks: help strings for traffic sent/recv appear swapped in wording: sent bytes help says bytes received, and recv bytes help says bytes sent. Histogram descriptor includes `le`, but `report_metrics` records histogram values through the metrics crate rather than exporting fixed bucket samples, so schema/collector semantics should be checked together.

Test signals: no local schema tests; bucket collector tests elsewhere likely assert descriptor-derived names and label behavior.
