
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/readonly.rs

## Purpose
`ReadOnlyBlockStore` wraps a low-level blockstore and forwards read calls while blocking all mutating calls by panicking. It is intended for read-only tools, with a TODO suggesting trait-level read-only APIs might be cleaner.

## Important APIs, Types, and Functions
- `ReadOnlyBlockStore::new(underlying)` returns `AsyncDropGuard<Self>`.
- Implements `BlockStoreReader` by delegating `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks`.
- Implements `BlockStoreDeleter::remove()` as `panic!("ReadOnlyBlockStore::remove blocked")`.
- Implements `OptimizedBlockStoreWriter` with delegated `allocate()` but panicking `try_create_optimized()` and `store_optimized()`.
- Async drop delegates to the underlying store.

## Control Flow
Read operations are transparent. Mutating operations fail immediately by panic, not by `Result::Err`. The wrapper still implements `LLBlockStore`, so callers that only have the full trait can compile mutating calls that panic at runtime.

## State and Persistence Behavior
No own persistence. It owns and drops the underlying store.

## Dependencies and Integration Points
Composes over any `LLBlockStore + OptimizedBlockStoreWriter`. Exported from the low-level implementations registry.

## Risks and Edge Cases
- Runtime panics for writes/removes are sharp edges in production paths.
- `allocate()` remains available and delegates to the underlying writer even though writes are blocked.
- No direct tests in this file validate panic behavior.

## Test Signals
No local tests. Behavior is likely exercised only indirectly where read-only wrappers are used by higher-level tools.
