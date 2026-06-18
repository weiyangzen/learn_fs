# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/PImpl.h

## Purpose
`PImpl.h` defines a minimal unique-ownership pimpl wrapper around `std::unique_ptr<T>`. It hides construction behind a static `create()` factory so callers can keep implementation storage opaque while still using pointer-like access.

## Important APIs, Types, And Functions
- `PImpl<T>` stores `std::unique_ptr<T> impl`.
- Private `ConstructorTag` disambiguates factory construction from the public default constructor.
- `create(args...)` forwards arguments to `std::make_unique<T>`.
- Dereference, arrow, and `get()` methods expose mutable and const `T` access.

## Control Flow And State
The default constructor leaves `impl` null. `create()` returns a fully constructed wrapper. Accessors do not guard against null, so callers must either use `create()` or explicitly handle default-initialized state before dereferencing.

## Persistence And External State
No persistence or serialization exists. Lifetime is RAII through `unique_ptr`; destruction of `PImpl` destroys the implementation.

## Dependencies And Integration Points
The only dependency is `<memory>`. It is suitable for headers that want to avoid including an implementation class definition while still keeping value-like ownership semantics.

## Risks And Edge Cases
The wrapper is move-only because `unique_ptr` is move-only. Null default state can cause crashes on `operator*` or `operator->`. There is no reset, release, swap, or explicit bool API, so consumers may need to use `get()` for presence checks.

## Test Signals
Compile tests should verify move-only behavior, factory forwarding, const and mutable accessors, destruction of owned objects, and expected failure or guarded behavior around default construction.
