# sources/sync-backup/kopia/repo/blob/webdav/webdav_storage_test.go

Purpose: validates the WebDAV provider against an optional external server and an in-process authenticated WebDAV server.

Important APIs/types/functions: `basicAuth`, `TestWebDAVStorageExternalServer`, `TestWebDAVStorageBuiltInServer`, `TestWebDAVStorageBuiltInServerWithMissingAsForbidden`, `transformMissingPUTs`, and `verifyWebDAVStorage`.

Control flow: external tests read URL/user/password from environment. Built-in tests serve a temp directory through `x/net/webdav` behind basic auth, run multiple shard configurations, clear existing blobs, run `blobtesting.VerifyStorage`, assert connection-info round trips, run provider validation, and close storage. The forbidden-missing test wraps PUT responses to convert 404 into 403 to exercise fallback directory creation.

State and persistence behavior: test blobs are stored in temp directories served over HTTP and removed between shard-spec runs.

Dependencies/integration: depends on `httptest`, `x/net/webdav`, provider-validation, blobtesting, and WebDAV provider code.

Risks and edge cases: external server tests are environment-gated. Built-in server behavior may not match every WebDAV implementation, so the 403 transform broadens coverage for common server quirks.

Test signals: success confirms authentication, sharded layout, provider validation, cleanup, and missing-parent retry behavior work over WebDAV.
