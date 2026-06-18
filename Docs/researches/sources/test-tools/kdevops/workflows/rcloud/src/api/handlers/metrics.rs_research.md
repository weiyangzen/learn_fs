<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs

## Purpose
This module implements the Prometheus scrape endpoint for rcloud.

## Important APIs and Functions
`metrics_handler(metrics)` receives `web::Data<Metrics>`, calls `metrics.encode()`, and returns a text response with content type `text/plain; version=0.0.4`.

## Control Flow
The handler logs access, encodes the registry, and returns HTTP 200. It does not update metrics itself.

## State, Persistence, and Dependencies
The state is the in-memory `Metrics` registry shared through Actix app data. There is no persistent metrics storage in this module. It depends on the local `metrics.rs` wrapper and Actix Web.

## Risks and Test Signals
Because most metric recording methods are currently unused in handlers, the scrape may show registered metrics but not meaningful request or VM operation counters. Tests should verify content type and that known metric names are present after `Metrics::new()`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/metrics.rs -->
