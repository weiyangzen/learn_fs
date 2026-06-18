# sources/storage-engines/foundationdb/flow/flow_future_support.swift

Purpose: placeholder Swift extension file for Flow future conformances shared by Flow-importing modules.

Important APIs/types/functions: commented examples for `FlowCallbackForSwiftContinuationCInt`, `FutureCInt`, `FlowCallbackForSwiftContinuationVoid`, and `FutureVoid` conforming to protocols from `future_support.swift`.

Control flow: no active executable declarations beyond `import Flow`.

State/persistence: no state.

Dependencies/integration: intended to sit beside generated C++/Swift interop future types and add conformances once those types can be extended cleanly.

Risks: because conformances are commented out, Swift future awaitability depends on other files/generated bindings. Stale comments can hide missing type coverage.

Test signals: compile-only; additional Swift future types should add active conformances here and be validated through `.value()` await usage.
