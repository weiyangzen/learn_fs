<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Optional.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Optional.h

Purpose: This header provides FoundationDB's legacy `Optional<T>` wrapper over `std::optional`. It preserves Flow conventions, especially assertion-based failure on absent `get()` rather than throwing `std::bad_optional_access`, and adds mapping helpers used widely in actor and data-structure code.

Important APIs and types: `Optional<T>` exposes `present`, `get`, `orDefault`, `withDefault`, `castTo`, `map`, `mapRef`, `flatMap`, `flatMapRef`, comparisons, pointer-like operators, `reset`, `hash`, and an arena-copy constructor. It inherits `ComposedIdentifier<T, 4>` for file identification. The header also defines `Traceable<Optional<T>>` and a `fmt::formatter` adapter.

Control flow: Map helpers either return an empty optional when absent or apply lambdas, member pointers, or member functions to the contained value. `mapRef` additionally treats present-but-null pointer-like values as absent. `flatMap` and `flatMapRef` remove one nested `Optional` level. `get()` uses `UNSTOPPABLE_ASSERT` to fail immediately if absent.

State and persistence behavior: Runtime state is a `std::optional<T>` member. Persistence behavior is delegated to serializer support elsewhere and to `ComposedIdentifier`. `orDefault` returns by value; `withDefault` mutates an absent optional and returns a reference to stored state.

Dependencies and integration points: It depends on `Traceable`, `FileIdentifier`, Swift bridging support, and `fmt`. It is foundational across Flow, including `NetworkAddressList`, TLS/system-monitor optional config fields, protocol messages, and metrics state.

Risks: `get()` aborts on absent values, so callers must check `present()` or rely on invariants. The removed conversion constructor note documents a historical pitfall around `Optional<Optional<T>>`; callers should use `castTo`. `compare` assumes `T` has `compare`, while `operator<` relies on `std::optional<T>` ordering.

Test signals: Useful tests include absent and present `map`/`flatMap` behavior, pointer-like `mapRef` null handling, `withDefault` mutation, move-qualified `get`, trace formatting for absent values, hash/equality behavior, and any serializer round trips involving optional fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Optional.h -->
