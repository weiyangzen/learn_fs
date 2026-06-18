# sources/user-network-fs/rclone/backend/sugarsync/sugarsync_internal_test.go

## Purpose

This file unit-tests SugarSync's HTML error parser.

## Important APIs, Types, and Functions

`TestErrorHandler` builds synthetic `http.Response` values with different bodies and checks `errorHandler` output strings.

## Control Flow

Each subtest creates a response body from a string, status code, and status text, then calls `errorHandler`. Cases cover empty body, unknown HTML, blank `<h3>`, and a real-looking `<h3>Can not move sync folder.</h3>` body.

## State and Persistence Behavior

No persistent state is used. Each response body is an in-memory `io.NopCloser`.

## Dependencies and Integration Points

It depends on `testify/assert`, `bytes`, `io`, and `net/http`. It tests the unexported parser in package `sugarsync`.

## Risks and Edge Cases

The parser only extracts the first non-empty `<h3>` content and does not decode HTML entities. Tests assert exact error strings, so status formatting changes will be caught.

## Test Signals

Passing tests indicate SugarSync API HTML failures produce useful errors instead of opaque raw bodies when an `<h3>` message is present.
