# sources/storage-engines/foundationdb/flow/flow_optional_support.swift

Purpose: bridges Flow C++ optional-like types into Swift `Optional`.

Important APIs/types/functions: protocol `FlowOptionalProtocol` with associated `Wrapped`, `present()`, and unsafe getter; `Swift.Optional.init(cxxOptional:)`.

Control flow: initializer checks `present()`. If false, it assigns `nil`; otherwise it reads the pointed-to wrapped value from `__getUnsafe().pointee`.

State/persistence: no state. It copies the pointed value into a Swift optional.

Dependencies/integration: imports `Flow`; C++ optional bridge types must conform to `FlowOptionalProtocol`.

Risks: explicitly uses `__getUnsafe` with a FIXME, so lifetime and pointer validity are caller/type dependent. Missing conformances mean the generic initializer is unavailable.

Test signals: Swift code constructing `Optional(cxxOptional:)` from Flow optional wrappers; compile and runtime memory safety are key checks.
