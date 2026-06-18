# sources/storage-engines/foundationdb/flow/include/flow/TypeTraits.h

## Purpose
Compile-time helpers for manipulating `std::variant` type lists.

## Important APIs, Types, And Functions
`variant_concat_t` and alias `variant_concat` concatenate two variant alternative lists. `variant_map_t` and alias `variant_map` apply a unary type-template to each alternative.

## Control Flow
All behavior occurs during template instantiation; there is no runtime flow.

## State And Persistence Behavior
No state or persistence. The generated variant types affect compile-time APIs and ABI of users.

## Dependencies And Integration Points
Depends only on `<variant>`. Integrates with generic serialization/RPC/template code that composes variant alternatives.

## Risks And Edge Cases
Use in common headers can increase compile times. Non-variant inputs fail with template diagnostics.

## Test Signals
`static_assert(std::is_same_v<...>)` tests for ordering and mapped alternatives cover the intended behavior.
