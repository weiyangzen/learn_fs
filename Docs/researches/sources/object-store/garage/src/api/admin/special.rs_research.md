## sources/object-store/garage/src/api/admin/special.rs

Purpose: implements public/special admin endpoints: CORS-ish `OPTIONS`, Prometheus metrics, basic health, and static website domain check.

Important APIs/types/functions: `RequestHandler` impls for `OptionsRequest`, `MetricsRequest`, `HealthRequest`, and `CheckDomainRequest`; private `check_domain`.

Control flow: `OptionsRequest` returns `200 OK` with `ALLOW`, `ACCESS_CONTROL_ALLOW_*`, and wildcard origin. `MetricsRequest` gathers from `admin.exporter.registry()` inside an OpenTelemetry span when the `metrics` feature is enabled; otherwise it returns bad request. `HealthRequest` maps `ClusterHealthStatus` to status/message, returning `503` only for unavailable quorum. `CheckDomainRequest` resolves a domain against S3 API root, S3 website root, or direct bucket name, then optionally requires bucket website config to exist.

State/persistence: read-only access to cluster health, config, bucket helper, and bucket website config.

Dependencies/integration: uses `Garage`, admin exporter, Prometheus feature gates, `host_to_bucket`, and admin request/response body aliases.

Risks: domain checking intentionally treats direct domains as website domains and requires website config. Metrics availability depends on build features. `OptionsRequest` is permissive and admin-specific, not bucket CORS-aware.

Test signals: no local tests. Functional confidence should come from health/metrics endpoint integration tests and config-driven website domain checks.
