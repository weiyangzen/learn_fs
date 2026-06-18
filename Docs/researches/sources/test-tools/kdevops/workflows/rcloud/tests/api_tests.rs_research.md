<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs -->
# sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs

## Purpose
This integration test validates the rcloud health endpoint through Actix's test harness.

## Important APIs and Functions
`test_health_check` initializes an `App` with `/api/v1/health` routed to `health::health_check`, sends a GET request, asserts the response status is successful, parses the body as JSON, and asserts `body["status"] == "healthy"`.

## Control Flow
The test is asynchronous under `#[actix_rt::test]`. It does not start a TCP listener; it exercises the service in memory.

## State, Persistence, and Dependencies
No persistent state is used. Dependencies include Actix Web test utilities, `web`, `App`, and the public library export `rcloud::api::handlers::health`.

## Risks and Test Signals
Coverage is intentionally narrow. It does not validate route registration through `configure_routes`, system status, metrics, images, or VM lifecycle endpoints. It is still a useful smoke test that the library module graph and health JSON contract compile and behave.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/tests/api_tests.rs -->
