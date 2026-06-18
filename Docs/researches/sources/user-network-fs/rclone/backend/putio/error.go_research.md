# sources/user-network-fs/rclone/backend/putio/error.go

## Purpose
Put.io retry/status helper: centralizes HTTP status validation and retry classification.

## Important APIs, Types, And Functions
Important surface: checkStatusCode, statusCodeError, Temporary, shouldRetry.

## Control Flow
SDK or direct HTTP errors are converted, 429 maps to pacer RetryAfter using x-ratelimit-reset or 60s, 5xx are temporary, context cancellation stops retry

## State And Persistence
no persistent state.

## Dependencies And Integration Points
go-putio, rclone fserrors/pacer, net/http.

## Risks And Test Signals
Risks and useful test signals: nil responses, stale reset headers, missing tests for malformed headers and SDK conversion.
