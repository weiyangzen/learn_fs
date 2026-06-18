<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h

Purpose: This header implements `ofats::any_invocable`, a C++ move-only type-erased callable similar to C++23 `std::move_only_function`/`std::any_invocable`. It supports cv/ref/noexcept-qualified function signatures.

Important APIs and flow: small nothrow-movable callables are stored in an inline two-pointer buffer; larger callables are heap allocated. Handler tables provide destroy, move, and call operations. Constructors accept callables or `std::in_place_type_t`, assignment swaps through temporaries, and `operator()` invokes the erased callable with signature-qualified constraints.

State and persistence: each object owns exactly one callable or is empty. Move construction transfers handler and storage, then clears the source handler. There is no global state.

Risks and test signals: calling an empty object dereferences a null call pointer. The large-handler move copies the pointer but relies on clearing the source handler to avoid double delete. Tests should cover small/large callables, move/swap, reference wrappers, noexcept signatures, ref-qualified invocation, exception propagation, and empty checks before calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h -->
