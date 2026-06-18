<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/errors.go -->
# sources/user-network-fs/go-nfs/errors.go

## Purpose
Defines RPC-level and NFS-level error types plus helpers for status bodies and write-error mapping.

## Important APIs, Types, and Functions
`RPCError`, `AuthError`, `RPCMismatchError`, `ResponseCodeProcUnavailableError`, `ResponseCodeSystemError`, `NFSStatusError`, `StatusErrorWithBody`, `errFormatterWithBody`, and `statusFromWriteError` are central.

## Control Flow
Handlers return ordinary errors or these typed errors. `conn.err` uses the active formatter to write RPC accept/deny status and optional NFS status body.

## State and Persistence Behavior
Errors are transient response state; formatter functions with prebuilt zero bodies are package-level constants.

## Dependencies and Integration Points
Integrated by every NFS handler via `w.errorFmt`, especially weak-cache-consistency and post-op-attr error replies.

## Risks and Edge Cases
`AuthError` and `RPCMismatchError` marshal little-endian while XDR is big-endian, likely wrong. Unknown errors collapse to system error, losing detail.

## Test Signals
Tests should assert wire bytes for each error class and procedure-specific error body length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/errors.go -->
