# sources/user-network-fs/rclone/fs/rc/params_test.go

## Purpose
This file verifies the typed RC parameter helpers and error classifiers defined in `params.go`.

## Important APIs, Types, and Functions
- Tests cover `ErrParamNotFound.Error`, `IsErrParamNotFound`, `NotErrParamNotFound`, `IsErrParamInvalid`, `Reshape`, `Params.Copy`, all core getters, and reserved HTTP request/response getters.
- Table-driven tests exercise accepted and rejected inputs for numeric, boolean, and duration parsing.

## Control Flow
Each test constructs small `Params` maps, calls the relevant helper, and asserts both value and error type/message. Duration tests rely on rclone `fs.ParseDuration` semantics, including `off`, years, days, months, and negative durations.

## State and Persistence
The tests are stateless except for local `httptest.NewRecorder` values used to validate `http.ResponseWriter` extraction.

## Dependencies and Integration Points
The tests use `testify/assert` and `testify/require`, the standard `net/http` test helpers, and `fs.Duration` parsing behavior. They document the contract consumed by RC server handlers and RC method implementations.

## Risks and Edge Cases
The tests intentionally allow float-to-int64 truncation and broad bool conversions, so future stricter behavior would need test changes. They verify error classification but do not exercise HTTP serialization directly; that appears in `rcserver` tests.

## Test Signals
Coverage is strong for parameter coercion and error typing. The main gaps are nested `Params.Copy` aliasing behavior and pathological JSON reshape cases beyond basic marshal/unmarshal failure.
