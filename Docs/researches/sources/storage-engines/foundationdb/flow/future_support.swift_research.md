# sources/storage-engines/foundationdb/flow/future_support.swift

Purpose: defines generic Swift protocols and await support for Flow future bridge types.

Important APIs/types/functions: `FlowCallbackForSwiftContinuationT`, `FlowFutureOps`, `FlowFutureOps.value()`, internal async property `waitValue`, and a `Flow.Void` specialization with `@discardableResult`.

Control flow: `.value()` awaits `waitValue`. If the future is already ready, it checks `isError`, throws `GeneralFlowError` for errors, asserts `canGet`, and returns `__getUnsafe().pointee`. If not ready, it creates a callback object and uses `withCheckedThrowingContinuation`, passing raw continuation and callback pointers to the C++ bridge callback `set`.

State/persistence: stack/local callback object and continuation wrapper are used during suspension. No durable state.

Dependencies/integration: imports `Flow` and requires concrete future/callback types to conform through associated types.

Risks: comments mark incomplete ready-error/cancellation handling and unsafe getter usage. Raw pointer handoff to C++ callback must preserve lifetime until continuation resumes.

Test signals: Swift `try await flowFuture.value()` for ready and pending futures; cancellation/error behavior needs explicit coverage.
