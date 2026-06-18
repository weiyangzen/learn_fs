
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/interface.rs

## Purpose
This file defines the low-level blockstore trait contract: asynchronous block reading/listing, writing, deletion, optimized prefix-aware data allocation, and the marker trait tying all pieces together.

## Important APIs, Types, and Functions
- `BlockStoreReader` exposes `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks`.
- `BlockStoreDeleter` exposes `remove`.
- `BlockStoreWriter` exposes slice-based `try_create` and `store`.
- `OptimizedBlockStoreWriter` defines associated `BlockData`, static `allocate(size)`, and optimized `try_create_optimized`/`store_optimized`.
- Blanket `impl BlockStoreWriter for B where B: OptimizedBlockStoreWriter + Sync` copies slices into allocated `BlockData` and calls the optimized methods.
- `LLBlockStore` is the marker trait requiring reader, writer, deleter, `AsyncDrop<Error = anyhow::Error>`, `Debug`, and `Any`.
- `block_data::IBlockData` and `create_block_data_wrapper!` provide crate-private wrappers around `Data` that preserve prefix-capacity invariants.

## Control Flow
The non-optimized writer API is layered over optimized allocation. `try_create()` and `store()` allocate exact user length, assert the exposed region length, copy user bytes into that region, and delegate. Implementations that need headers allocate larger physical buffers and shrink the visible region so later prefix growth does not reallocate.

## State and Persistence Behavior
No state here. It defines the behavioral and memory-layout contracts that persistence implementations must respect.

## Dependencies and Integration Points
Depends on `async_trait`, `futures::stream::BoxStream`, `byte_unit::Byte`, `cryfs_utils::data::Data`, and crate result enums. Every low-level implementation and adapter in this subset implements these traits.

## Risks and Edge Cases
- The macro implementation body uses `impl AsRef<[u8]> for BlockData` rather than `$name`; this works for invocations naming the wrapper `BlockData`, but the macro is less general than its parameter suggests.
- `IBlockData::new()` is crate-private and unchecked by design; safety depends on only local implementations constructing valid wrappers.
- The blanket writer copies user slices, so optimized no-copy behavior is only available to callers that use optimized APIs directly.

## Test Signals
No local tests. The common low-level test suite exercises the trait contract through concrete implementations; optimized writer behavior is marked as a TODO in tests.
