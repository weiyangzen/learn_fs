# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/allocator_constructed.hpp

Purpose: RAII helper for constructing a stack-resident object through an allocator and destroying it reliably.

Important APIs, types, and functions: Defines `allocator_policy` with `construct` and `destroy`, and `allocator_constructed<Allocator,T,Policy>` with constructor, destructor, and `value()`.

Control flow: The constructor stores an allocator copy and calls `Policy::construct` on an `opt_storage<T>` address. The destructor calls `Policy::destroy`. `value()` returns the live object reference.

State and persistence behavior: Owns a single object lifetime in local storage plus an allocator copy. It never allocates its own storage.

Dependencies and integration points: Uses `boost/core/allocator_traits.hpp` and unordered `opt_storage`. FOA insertion paths use similar allocator-aware construction patterns to preserve allocator semantics.

Risks: The class assumes construction succeeds; if `Policy::construct` throws, the destructor is not run and no object exists, which is normal C++ construction behavior. Copy/move are not explicitly disabled, so use as a local non-copied guard.

Test signals: Allocator-aware tests should verify construct/destroy calls and behavior with custom policies.
