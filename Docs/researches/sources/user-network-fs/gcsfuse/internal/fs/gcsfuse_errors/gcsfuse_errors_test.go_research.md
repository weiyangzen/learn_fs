<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go

## Purpose

This test file verifies the behavior of `FileClobberedError`, especially its user-facing string and wrapped error compatibility.

## Important APIs, Types, and Functions

`TestFileClobberedError` is a table-driven testify test. It constructs `FileClobberedError` values with object names and either a concrete underlying error or nil, compares `Error()` output, and checks `errors.Is` for the non-nil case.

## Control Flow

Each test case builds the error, calls `Error()`, compares the resulting string, and conditionally asserts standard wrapping behavior. The nil-underlying-error case verifies that the formatter still produces a stable `<nil>` suffix.

## State and Persistence Behavior

There is no external state. Test data is local to the table.

## Dependencies and Integration Points

The file depends on Go `errors`, `fmt`, `testing`, and `github.com/stretchr/testify/assert`. It protects the contract consumed by higher-level fs code that may match underlying errors after wrapping them in a clobbering diagnostic.

## Risks and Edge Cases

The test intentionally locks the full error string, making wording changes visible. It only checks `errors.Is` for non-nil causes and does not check `errors.As` or behavior when the wrapped error type has custom matching.

## Test Signals

Signals are narrow and strong: exact formatting and unwrap semantics for `FileClobberedError`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go -->
