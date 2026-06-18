# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/type_traits.hpp

## Purpose

This header collects Boost.Unordered-specific type traits and compatibility aliases. It fills gaps across C++ standards and old standard libraries, supports transparent lookup constraints, and provides deduction-guide helper traits for unordered container constructors.

## Important APIs, types, and functions

General utilities include `type_identity`, `make_void`, `void_t`, `is_complete`, `is_complete_and_move_constructible`, `remove_cvref_t`, `is_similar`, `is_similar_to_any`, and a pre-C++17 `as_const` fallback.

Compatibility aliases provide `is_trivially_default_constructible`, `is_trivially_copy_constructible`, and `is_trivially_copy_assignable`, using old libstdc++ `std::has_trivial_*` traits when modern traits are unavailable.

`is_nothrow_swappable<T>` detects whether unqualified `swap(T&, T&)` is available and `noexcept`. The implementation uses ADL through `using std::swap`.

Transparent lookup helpers include `is_transparent<T>`, `are_transparent<Key, Hash, KeyEqual>`, and `transparent_non_iterable<Key, UnorderedMap>`. The latter ensures heterogeneous lookup is enabled only when both hash and equality are transparent and the key is not convertible to iterator types.

When `BOOST_UNORDERED_TEMPLATE_DEDUCTION_GUIDES` is enabled, deduction-guide helpers include `is_input_iterator_v`, `is_allocator_v`, `is_hash_v`, `is_pred_v`, `iter_key_t`, `iter_val_t`, and `iter_to_alloc_t`.

## Control Flow

All behavior is compile-time template selection. Preprocessor gates enable C++17 deduction-guide helpers when supported and select old libstdc++ fallbacks with `BOOST_WORKAROUND`. SFINAE through `void_t` controls trait specialization.

## State and Persistence Behavior

There is no runtime state. The file defines types, aliases, and constants consumed at compile time by container templates.

## Dependencies and Integration Points

The header depends on Boost.Config, Boost workaround macros, `<type_traits>`, `<utility>`, and `<iterator>` when deduction guides are supported. It is an integration point for Boost.Unordered container overload participation, heterogeneous lookup, allocator/hash/predicate disambiguation, swap exception specifications, and older compiler support.

## Risks and Edge Cases

Traits that inspect incomplete types must avoid instantiating standard traits on incomplete inputs; `is_complete_and_move_constructible` handles that with `std::conditional`. Transparent lookup constraints must avoid accepting iterator-like keys, or overloads can become ambiguous. Deduction guide heuristics intentionally approximate standard requirements, so unusual iterators, allocators, or hash-like integral types can expose edge cases. Old libstdc++ fallbacks rely on deprecated compiler traits.

## Test Signals

Compile tests should cover incomplete types, ADL swap with throwing and non-throwing overloads, transparent hash/equality with heterogeneous keys, iterator-convertible keys rejected from heterogeneous overloads, and deduction-guide construction from iterators and allocators. Cross-toolchain CI on old libstdc++, C++11/14/17/20 modes, and MSVC is particularly valuable.
