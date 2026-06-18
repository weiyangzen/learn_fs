# sources/user-network-fs/rclone/fs/rc/params.go

## Purpose
This file defines `rc.Params`, the common input/output map used by rclone remote-control calls, plus typed getters and standard error response construction.

## Important APIs, Types, and Functions
- `type Params map[string]any` is the canonical RC payload shape.
- `ErrParamNotFound` and `ErrParamInvalid` distinguish missing parameters from malformed parameters; these are later translated to HTTP 400.
- `Reshape(out, in any) error` converts arbitrary structured values through JSON marshal/unmarshal.
- Getter methods include `Get`, `GetString`, `GetInt64`, `GetFloat64`, `GetBool`, `GetStruct`, `GetStructMissingOK`, `GetDuration`, `GetFsDuration`, `GetHTTPRequest`, and `GetHTTPResponseWriter`.
- `Error(path, in, err, status)` creates the standard RC JSON error body and adjusts status for not-found and parameter errors.

## Control Flow
Most getters call `Get`, type-switch the result, and return either a typed value or `ErrParamInvalid`. Numeric and boolean getters accept strings and selected numeric types. `GetStruct` first uses `Reshape`; if the raw value is a string and reshape fails, it tries to unmarshal the string as JSON. `Error` prioritizes filesystem not-found errors and RC parameter errors over the supplied status code.

## State and Persistence
The code is stateless except for shallow copying a `Params` map with `Copy`. `GetHTTPRequest` and `GetHTTPResponseWriter` rely on server-injected reserved keys `_request` and `_response`.

## Dependencies and Integration Points
It is used by RC functions, the HTTP server, WebGUI plugin RC methods, sync RC methods, and the WASM bridge. It depends on `encoding/json`, `net/http`, `strconv`, `time`, and `fs.ParseDuration`.

## Risks and Edge Cases
`Params.Copy` is shallow, so nested maps/slices remain shared. `GetInt64` converts `float64` by truncation after only range checking, which matches JSON number handling but may surprise callers expecting integral validation. `Reshape` is convenient but can be expensive and may silently apply JSON type coercions. Reserved keys can carry raw HTTP interfaces into RC handlers and must not be serialized back accidentally in error input; the server copies the original input before injecting them.

## Test Signals
`params_test.go` covers missing/invalid errors, reshape failures, shallow copy behavior, string/int/float/bool/duration parsing, struct extraction including JSON strings, optional struct reads, and reserved HTTP request/response retrieval.
