# sources/user-network-fs/rclone/backend/webdav/api/types_test.go

Purpose: unit-test `Prop.StatusOK`.

Important APIs: `TestPropStatusOK` table covering empty status, 200, 404, mixed 404/200, mixed 200/404, and all non-2xx.

Control flow/state: each subtest constructs a `Prop` and compares `StatusOK()` to the expected value.

Dependencies/integration: standard `testing`; protects logic used by WebDAV listing, metadata reads, and PROPPATCH responses.

Risks/test signals: ensures optional 404 propstats do not hide valid 2xx property data.
