# sources/storage-engines/rocksdb/util/overload.h

## Purpose
Provides a compact C++ helper for combining several function objects into one overload set, most commonly for `std::visit` over variants.

## Important APIs, Types, And Functions
`template <typename... Ts> struct overload : Ts...` inherits every functor and imports each `operator()` via a pack expansion. The class template argument deduction guide `overload(Ts...) -> overload<Ts...>` lets callers write `overload{lambda1, lambda2}` without naming template parameters.

## Control Flow
There is no runtime control flow beyond normal overload resolution. Construction stores the provided base functors and invocation dispatches to the matching inherited call operator.

## State And Persistence
State is exactly the captured state of the supplied functors. The helper owns that state by value through base subobjects and has no persistence behavior.

## Dependencies And Integration Points
Only depends on RocksDB namespace definition. It integrates with modern C++ code using variants or visitors and avoids writing bespoke visitor structs.

## Risks
Ambiguous overloads or overlapping generic lambdas can still produce compile errors. Since functors are inherited by value, large captures or reference lifetimes remain the caller's responsibility.

## Test Signals
No direct tests in this subset. Compile-time use sites are the primary signal; failures generally appear as overload-resolution or lifetime bugs in callers.
