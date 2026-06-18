
# sources/security-integrity/cryfs/crates/blockstore/src/overhead.rs

## Purpose
`Overhead` models the per-block physical bytes not available to callers, allowing layered blockstores to convert between physical block size and usable block size.

## Important APIs, Types, and Functions
- `Overhead { overhead: Byte }` is `Copy`, `Clone`, `PartialEq`, `Eq`, and `Debug`.
- `impl Add for Overhead` sums overheads with `Byte::add().unwrap()`.
- `Overhead::new(overhead)` constructs a wrapper.
- `usable_block_size_from_physical_block_size(physical)` subtracts overhead or returns `InvalidBlockSizeError`.
- `physical_block_size_from_usable_block_size(usable)` adds overhead.
- `InvalidBlockSizeError` is `derive_more::Error + Display` with a message.

## Control Flow
Conversion is straightforward arithmetic. Physical-to-usable uses checked subtraction and produces an explanatory error when physical size is smaller than overhead. Usable-to-physical and overhead addition unwrap `Byte::add()`.

## State and Persistence Behavior
No persistence. The type is a value object returned by blockstore layers such as on-disk and integrity; layered stores add their overheads together.

## Dependencies and Integration Points
Depends on `byte_unit::Byte` and `derive_more`. Called throughout low-level and high-level tests to verify size conversion invariants.

## Risks and Edge Cases
- `Byte::add().unwrap()` can panic on overflow.
- The doc comment says "call sits", likely a typo for "call sites" or "callers".
- `InvalidBlockSizeError` exposes only the formatted message, not structured physical/overhead values.

## Test Signals
Unit tests cover successful subtraction, zero usable size, error when physical is smaller than overhead, usable-to-physical addition, and round-trip conversions in both directions.
