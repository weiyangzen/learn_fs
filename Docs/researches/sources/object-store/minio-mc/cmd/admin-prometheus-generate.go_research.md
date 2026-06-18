# sources/object-store/minio-mc/cmd/admin-prometheus-generate.go

## Purpose
Implements `mc admin prometheus generate`, producing Prometheus scrape configuration for MinIO metrics endpoints.

## Important APIs, types, and functions
Important symbols are `defaultJobName`, `metricsV2BasePath`, `prometheusFlags`, `adminPrometheusGenerateCmd`, `PrometheusConfig`, `StatConfig`, `ScrapeConfig`, `checkAdminPrometheusSyntax`, `generatePrometheusConfig`, and `mainAdminPrometheusGenerate`.

## Control flow
The handler validates target plus optional metric type, cleans and validates the alias, reads host config, parses its URL, chooses v2 or v3 metrics path and job name, optionally generates a bearer token, fills scheme and host target, and prints YAML or JSON through `printMsg`.

## State and persistence behavior
No repo or server state is persisted. It reads local alias configuration and may generate a long-lived Prometheus JWT unless `--public` is used.

## Dependencies and integration points
It integrates alias config lookup, Prometheus token generation, v2/v3 metrics validators, YAML/JSON serialization, console colorization, and global output flags.

## Risks and edge cases
The generated default token expiry is very long. `--public` omits bearer token and assumes public metrics access. v2 rejects v3-only flags, and v3 bucket paths are limited to specific subsystems.

## Test signals
Tests should cover invalid aliases, missing host config, v2 default and subsystem paths, v3 default/subsystem/bucket paths, public token omission, YAML and JSON output, and invalid API version handling.
