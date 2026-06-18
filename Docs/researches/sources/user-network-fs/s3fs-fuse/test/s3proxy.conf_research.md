# sources/user-network-fs/s3fs-fuse/test/s3proxy.conf

## Purpose
Default S3Proxy configuration for local integration tests with both HTTP and HTTPS endpoints.

## Important APIs, Types, And Control Flow
Sets HTTP endpoint `127.0.0.1:8081`, HTTPS endpoint `127.0.0.1:8080`, AWS v2/v4 auth, local identity/credential, keystore path/password, and transient-nio2 jclouds backend credentials.

## State And Persistence
No mutable state in the file. At runtime S3Proxy uses an in-memory/transient backend and the generated keystore.

## Dependencies And Integration Points
Read by Java S3Proxy in `integration-test-common.sh` unless public/noauth or chaos proxy variants are selected. Coordinates with credentials file and s3fs `-o url` defaults.

## Risks And Test Signals
Ports and credentials are fixed test defaults. HTTPS relies on generated `/tmp/keystore.jks`. Successful bucket creation/head/copy through S3Proxy validates this config.
