# sources/storage-engines/rocksdb/include/rocksdb/functor_wrapper.h

## Purpose

`functor_wrapper.h` is a small C++11 compatibility helper used to store a typed callable and its arguments behind a raw `void*` thread entry point. In this source set it supports `Env::StartThreadTyped`.

## Important APIs, types, and functions

The `detail` namespace implements a compile-time index sequence: `IndexSequence`, recursive `IndexSequenceHelper`, `make_index_sequence`, and overloaded `call` helpers that expand tuple elements into a callable. `FunctorWrapper<Args...>` stores `std::function<void(Args...)>` and `std::tuple<Args...>`, and exposes `invoke()` to call the function with the stored tuple values.

## Control flow and behavior

`Env::StartThreadTyped` constructs a `FunctorWrapper` with a callable and forwarded arguments, passes it to `StartThread` as a raw pointer, and uses a trampoline to call `invoke()` and delete the wrapper after the thread function returns. `detail::call` computes tuple size at compile time, builds an index sequence, and expands `std::get<I>(t)...` into the stored function.

## State and persistence

The wrapper owns only transient in-memory state for a scheduled thread invocation: the `std::function` and copied or moved argument tuple. It has no persistence behavior. Ownership is manual because it is passed through a C-style `void*` API; deletion is expected in the trampoline.

## Dependencies and integration points

The header depends on `<functional>`, `<memory>`, `<utility>`, tuple support through included standard headers, and RocksDB namespace definitions. Its practical integration point is `env.h`, where it adapts typed C++ callables to the raw function pointer API exposed by `Env::StartThread`.

## Risks and test signals

Argument lifetime and move/copy semantics are the main risks. The constructor stores `Args...` in a tuple, so references and move-only arguments need careful template behavior. If the trampoline is bypassed or thread creation fails after allocation, the wrapper could leak. Tests should cover typed thread launch with multiple arguments, moved values, reference-like wrappers if supported, deletion after invocation, and exception policy alignment because exceptions must not escape into RocksDB.
