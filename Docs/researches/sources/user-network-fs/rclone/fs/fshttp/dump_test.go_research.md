<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dump_test.go -->
# sources/user-network-fs/rclone/fs/fshttp/dump_test.go

## Purpose
Tests HTTP dump logging behavior for retryable errors and trace logging.

## Important APIs, Types, And Control Flow
`TestIsRetryableResponse` checks transport errors and selected HTTP status codes. `TestDumpErrors` uses an httptest server and captured slog output to verify `--dump errors` gates request/response/curl dumps to retryable responses, with body inclusion controlled by `DumpBodies`. `TestDumpTrace` verifies `DumpTrace` emits httptrace events for HTTP and HTTPS without dumping bodies.

## State And Persistence
Temporarily replaces the global logger and mutates global config dump/log/insecure flags, restoring them in defers. Starts ephemeral HTTP/TLS servers and resets transports around trace tests.

## Dependencies And Integration Points
Exercises fshttp client construction, dump flags from `fs/dump.go`, retryable response classification, slog logging, and httptrace integration.

## Risks And Test Signals
Strong signal for logging gates. It does not verify exact full dump text, only key substrings, and depends on transport reuse for one trace assertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dump_test.go -->
