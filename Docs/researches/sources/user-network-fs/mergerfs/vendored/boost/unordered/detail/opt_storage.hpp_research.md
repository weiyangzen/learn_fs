# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/opt_storage.hpp

## Purpose

This Boost.Unordered detail header defines an uninitialized storage wrapper for optional-like object lifetime management. It gives implementation code a place to store a `T` without constructing or destroying it automatically.

## Important APIs, types, and functions

`template<class T> union opt_storage` contains one member, `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS T t_`. The default constructor and destructor are intentionally empty. `address()` and `address() const` return `std::addressof(t_)`, avoiding overloaded `operator&`.

## Control Flow

The type has no runtime branching. Its behavior is controlled by C++ union lifetime rules: construction, destruction, and assignment of the contained `T` are the responsibility of the owning optional-like structure.

## State and Persistence Behavior

`opt_storage` stores raw object storage only. It does not track whether `t_` is live. Any surrounding container must maintain engagement state and must explicitly construct and destroy `T` at `address()`.

## Dependencies and Integration Points

It includes `boost/config.hpp` for `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS` and `<memory>` for `std::addressof`. It integrates with Boost.Unordered internals that need compact optional storage for node buffers or metadata without pulling in `std::optional` or imposing automatic lifetime behavior.

## Risks and Edge Cases

The main risk is lifetime misuse. Reading `t_` before placement construction or failing to destroy a live non-trivial `T` is undefined behavior. The empty destructor makes leaks of non-trivial `T` invisible to the type system. `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS` can affect layout and should be validated on supported compilers.

## Test Signals

Tests should exercise construction and destruction by the owning wrapper, especially for non-trivial types with counters. Layout-sensitive tests can check size reductions for empty types where the attribute is supported. Sanitizer runs are useful because misuse normally appears as lifetime or leak errors rather than local assertion failures.
