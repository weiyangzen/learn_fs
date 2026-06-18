# sources/user-network-fs/s3fs-fuse/test/s3proxy_http.conf

## Purpose
S3Proxy configuration variant for HTTP-only proxy tests.

## Important APIs, Types, And Control Flow
Sets the HTTP endpoint on `127.0.0.1:8080`, AWS v2/v4 auth, local identity/credential, and transient jclouds backend identity/credential.

## State And Persistence
No local state; S3Proxy owns transient object data while running.

## Dependencies And Integration Points
Selected by `integration-test-common.sh` when Chaos HTTP Proxy is enabled. It avoids HTTPS because the chaos proxy path is HTTP-only.

## Risks And Test Signals
Port 8080 overlaps with the HTTPS port in the default config but is used in a mutually exclusive config path. Test signal is successful proxy-mediated S3 operations with injected failures.
