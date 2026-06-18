# sources/user-network-fs/rclone/backend/union/errors.go

Purpose: multi-error helper for aggregating per-upstream union operation failures.

Important APIs: `Errors` (`[]error`) with `Map`, `FilterNil`, `Err`, `Error`, and `Unwrap`.

Control flow/state: callers allocate indexed slices, fill errors from concurrent branches, filter nils, and return either nil or the aggregate. `Unwrap() []error` enables `errors.Is`/`errors.As` across contained errors.

Dependencies/integration: standard `bytes` and `fmt`; used throughout union fan-out operations, listing reconciliation, shutdown, cleanup, and upload teeing.

Risks/test signals: positional context is lost after filtering unless callers wrap messages with upstream names. `errors_test.go` covers map/filter/error string/unwrapping semantics.
