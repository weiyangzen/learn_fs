# sources/storage-engines/rocksdb/util/cast_util.h

Purpose: collects small casting and pointer helpers used to make potentially unsafe conversions explicit. It supports checked static casts for legacy downcasts, lossless integral casts, initializer-list disambiguation, and non-owning optional references.

Important APIs and types: `static_cast_with_check<DestClass>(SrcClass*)` performs `static_cast` and, when RTTI is enabled, asserts equality with `dynamic_cast`. The shared-pointer overload uses `std::static_pointer_cast` and debug RTTI validation. `lossless_cast<To>(From)` supports integral or enum value casts when the destination is at least as large, and pointer reinterpret casts between integral/enum pointee types with equal size. `List<T>` returns a homogeneous `initializer_list` reference. `UnownedPtr<T>` wraps a raw pointer with `get`, `operator->`, `operator*`, and bool conversion without ownership semantics.

Control flow and state: most checks are compile-time `static_assert`s. Runtime validation exists only for RTTI-enabled checked casts. `UnownedPtr` stores a nullable raw pointer and does not manage lifetime.

Dependencies and integration: depends on `<initializer_list>`, `<memory>`, `<type_traits>`, and RocksDB namespace headers. `coding.h` uses `lossless_cast` for byte pointer conversions in varint code.

Risks and test signals: `static_cast_with_check` can still be unsafe in non-RTTI builds if the caller's type assumption is wrong. `lossless_cast` checks type size, not signed range of runtime values, so signed-to-unsigned semantic surprises remain possible. The pointer branch has a likely typo checking `std::is_enum_v<To>` instead of the destination dereferenced type, though integral destination pointers satisfy the other condition. `UnownedPtr` can dangle. No direct tests in this subset.
