# sources/storage-engines/foundationdb/flow/reply_support.swift

## Purpose
This Swift file provides a small async helper protocol for Flow reply promises. It lets a generated or wrapped `ReplyPromise` complete itself from an async Swift closure, bridging Swift concurrency into Flow's reply-sending API.

## Important APIs, Types, And Functions
`_FlowReplyPromiseOps` defines associated type `_Reply`, async method `with(_ makeReply: () async -> _Reply)`, and low-level `send(_ value: inout _Reply)`. The protocol extension provides the default `with` implementation: await the closure, store the reply in a mutable local, then call `send(&rep)`. The method is annotated with `@_unsafeInheritExecutor`.

## Control Flow
Callers invoke `with` with an async closure that creates the reply value. Execution awaits the closure on the inherited executor, then sends the completed reply by inout reference to the conforming Flow promise wrapper. There is no branching beyond the await/send sequence.

## State And Persistence
The only local state is the temporary mutable reply value. Persistent state belongs to the conforming `ReplyPromise` implementation and the Flow runtime receiving the sent reply. No file-level globals or caches exist.

## Dependencies And Integration Points
The file imports `Flow` and is intended for generated Swift/C++ interop types that can conform to `_FlowReplyPromiseOps`. The TODO notes that direct `ReplyPromise` extension is blocked until template support improves, so this protocol is an adaptation layer for generated wrappers.

## Risks
`@_unsafeInheritExecutor` is an underscored Swift attribute and ties the code to compiler/runtime behavior. The closure cannot throw, so error replies need a separate representation. The inout send requires the reply value to remain valid for whatever C++ interop code does during the call. Conformers must implement `send` exactly once per reply to avoid duplicate or missing completions.

## Test Signals
Swift interop tests should verify that an async closure completes a Flow reply, that executor inheritance does not deadlock the Flow network thread, and that generated promise wrappers send exactly the produced value. Negative/error-path coverage belongs in higher-level wrappers because this helper only supports nonthrowing reply construction.
