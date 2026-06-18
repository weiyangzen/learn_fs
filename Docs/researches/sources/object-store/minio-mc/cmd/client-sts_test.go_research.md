# sources/object-store/minio-mc/cmd/client-sts_test.go

## Purpose

`client-sts_test.go` validates that mc can obtain web-identity STS credentials from environment-driven configuration and use them for both S3 object operations and admin operations.

## Important APIs, Control Flow, And State

`TestSTSS3Operation` writes a JWT to a temp file, exposes a fake STS endpoint with `stsHandler`, sets `MC_STS_ENDPOINT_test` and `MC_WEB_IDENTITY_TOKEN_FILE_test`, creates an S3 client with alias `test`, and verifies a PUT succeeds against the object httptest server. `TestAdminSTSOperation` performs the same STS setup, creates an admin client with debug/insecure enabled, and calls `AddCannedPolicy` against a fake admin handler. These tests exercise `Config.getCredsChain`, which sets AWS web identity environment variables and prepends IAM/STS credentials ahead of static credentials.

## Dependencies, Risks, And Signals

Dependencies include `httptest`, temp files, environment mutation through `t.Setenv`, and handlers from nearby S3/admin tests. The tests signal that alias-scoped STS env vars are wired into minio-go credential resolution. Risks are process-wide AWS env mutation in `getCredsChain`, endpoint parsing failures, and interactions between debug transport and STS transport reuse.
