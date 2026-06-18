# sources/test-tools/syzkaller/pkg/html/urlutil/urls.go

## Purpose
`urls.go` provides small helpers for manipulating query parameters in dashboard URLs.

## Important APIs, Types, And Functions
`SetParam(baseURL, key, value)` sets a query parameter to a single value or removes it when `value` is empty. `DropParam(baseURL, key, value)` removes either all values for a key or only matching key-value pairs. `TransformParam(baseURL, key, f)` is the generic primitive that passes existing values to a transformer and writes the returned values back.

## Control Flow
`SetParam` delegates to `TransformParam` with a transformer that returns nil for empty values or a one-element slice otherwise. `DropParam` delegates with a transformer that returns nil for remove-all or filters out values equal to the requested value. `TransformParam` returns empty string for empty or unparsable URLs, parses the URL, obtains `url.Values`, transforms `values[key]`, deletes the key if the returned slice is empty, otherwise assigns the returned slice, re-encodes the query, and returns the serialized URL.

## State And Persistence Behavior
All behavior is pure string transformation. There is no persistent state. Query encoding may normalize parameter ordering and escaping according to `net/url.Values.Encode`.

## Dependencies And Integration Points
The file depends only on Go `net/url`. It is intended for HTML/dashboard code that needs to build filter, toggle, or navigation URLs.

## Risks And Edge Cases
The helper treats empty output from the transformer as deletion, so callers cannot intentionally keep a key with zero values. Parse errors and empty input collapse to an empty string, which may hide bad caller input. `SetParam` overwrites duplicate values by design. Query parameter order is canonicalized by `Encode`, which can change visual URL ordering.

## Test Signals
`urls_test.go` covers `DropParam` for all-values and single-value removal with duplicate keys. Additional useful tests would cover `SetParam`, invalid URLs, encoding behavior, and transformer functions that preserve multiple values.
