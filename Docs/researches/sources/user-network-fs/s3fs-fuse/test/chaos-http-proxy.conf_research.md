# sources/user-network-fs/s3fs-fuse/test/chaos-http-proxy.conf

## Purpose
Configuration for Chaos HTTP Proxy during proxy-failure integration tests.

## Important APIs, Types, And Control Flow
Defines a simple response distribution: one HTTP 503 response for every nine successes through `com.bouncestorage.chaoshttpproxy.http_503=1` and `success=9`.

## State And Persistence
No runtime state in the file itself. The Java proxy reads it at startup and injects transient failures into HTTP traffic.

## Dependencies And Integration Points
Used by `integration-test-common.sh` when `CHAOS_HTTP_PROXY` or `CHAOS_HTTP_PROXY_OPT` is set. It sits between s3fs and S3Proxy on HTTP-only test runs.

## Risks And Test Signals
The tiny config assumes Chaos HTTP Proxy property names and a fixed failure ratio. It does not configure ports here, so defaults or companion proxy behavior must match the script’s wait on port 1080. Test signal is successful retry behavior under injected 503s.
