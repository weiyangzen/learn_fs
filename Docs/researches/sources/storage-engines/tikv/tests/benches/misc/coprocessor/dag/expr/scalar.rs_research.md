# sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/scalar.rs

## Purpose
This microbenchmark compares scalar-function argument-count lookup by `match` versus `HashMap`.

## Important APIs, Types, and Functions
`get_scalar_args_with_match` matches selected `ScalarFuncSig` variants to min/max argument counts. `init_scalar_args_map` builds an equivalent map for selected signatures plus a default-like entry. `get_scalar_args_with_map` looks up values or returns `(0, 0)`. Two `#[bench]` functions call the match or map path 1000 times.

## Control Flow
The map benchmark initializes the map once before iteration. Both benches black-box the signature and result while repeatedly querying `ScalarFuncSig::AbsInt`, which falls through to default in the match path and misses in the map path.

## State and Persistence Behavior
State is an in-memory map for one benchmark. No persistence.

## Dependencies and Integration Points
It depends on TiKV `collections::HashMap`, nightly `test`, and `tipb::ScalarFuncSig`. It informs performance tradeoffs for expression metadata lookup designs.

## Risks and Test Signals
The tested signature set is small and synthetic, so results should not be overgeneralized. Enum evolution may require updating representative cases.
