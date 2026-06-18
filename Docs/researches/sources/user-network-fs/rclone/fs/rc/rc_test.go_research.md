# sources/user-network-fs/rclone/fs/rc/rc_test.go

## Purpose
This file validates the RC JSON response writer.

## Important APIs, Types, and Functions
- `TestWriteJSON` writes a small `Params` map to a buffer and asserts the exact tab-indented JSON output.

## Control Flow
The test calls `WriteJSON`, requires no error, and compares the resulting buffer to a golden string.

## State and Persistence
No persistent state is touched.

## Dependencies and Integration Points
It depends on `bytes.Buffer` and `testify`. It protects HTTP API response formatting used by `rcserver.writeError` and successful RC POST responses.

## Risks and Edge Cases
The exact string assertion makes formatting changes deliberate but may be brittle if Go's JSON map ordering behavior or encoder formatting changes. It does not cover write failures.

## Test Signals
The test is narrow but useful: it documents that RC responses are pretty-printed with tabs and include a trailing newline.
