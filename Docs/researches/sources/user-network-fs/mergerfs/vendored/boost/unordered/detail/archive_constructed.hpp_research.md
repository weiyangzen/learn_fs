# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/archive_constructed.hpp

Purpose: RAII helper for loading an object from a Boost.Serialization archive into uninitialized stack storage.

Important APIs, types, and functions: Defines noncopyable `archive_constructed<T>` with `archive_constructed(name, ar, version)`, destructor, and `get()`.

Control flow: Construction calls `core::load_construct_data_adl` on the storage address, then deserializes an NVP into `get()`. If archive extraction throws, it explicitly destroys the partially constructed object and rethrows. Destructor destroys the loaded object.

State and persistence behavior: Owns one temporary `T` in `opt_storage<T>` until consumed by table loading. It does not persist archive data.

Dependencies and integration points: Uses Boost.Core serialization hooks, no-exceptions support macros, `noncopyable`, and `opt_storage`. `concurrent_table` uses it when loading set values and map keys/mapped values.

Risks: Correctness depends on archive `load_construct_data` constructing a valid object at the storage address. Strict-aliasing diagnostics are suppressed for affected GCC versions around `get()`.

Test signals: Serialization tests should cover throwing archives, non-default-constructible value types, and object-address reset paths.
