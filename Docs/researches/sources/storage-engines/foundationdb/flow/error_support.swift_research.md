# sources/storage-engines/foundationdb/flow/error_support.swift

Purpose: adds Swift convenience behavior for Flow errors.

Important APIs/types/functions: extension `Flow.Error.isEndOfStream`.

Control flow: property compares `self.code()` to `error_code_end_of_stream`.

State/persistence: no state.

Dependencies/integration: imports `Flow` and uses generated/imported Flow error constants. It is intended for Swift callers consuming Flow streams or futures.

Risks: only covers one error classification. Any change to generated symbol names or error code bridging breaks compilation.

Test signals: Swift code can branch on `error.isEndOfStream` instead of manually comparing codes.
