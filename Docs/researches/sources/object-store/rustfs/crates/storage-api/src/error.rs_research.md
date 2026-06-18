# sources/object-store/rustfs/crates/storage-api/src/error.rs

## Purpose
Provides stable storage error codes and a default `StorageResult` alias for cross-crate storage contracts.

## Important APIs and Types
`StorageErrorCode` enumerates disk, volume, bucket, object, multipart, erasure quorum, decommission, rebalance, cancellation, and namespace lock errors. `as_u32` maps each variant to a stable hexadecimal code. `from_u32` decodes known codes to variants and returns `None` for unknown values. `StorageResult<T, E = StorageErrorCode>` defaults result errors to this code enum.

## Control Flow and State
The mapping is entirely const match logic with no persistence in this module. Stability of numeric codes is the core persistence contract because codes may be serialized or passed over boundaries elsewhere.

## Integration Points
Re-exported by `storage-api/src/lib.rs`. Backend and admin API crates can use numeric codes for wire-safe or storage-safe error representation without depending on concrete error types.

## Risks
There are gaps at `0x2B` and `0x2C`, and code assignments must not be reused accidentally. The enum does not implement `Display`, `Error`, or serde here, so adapters must add presentation/wire conversion. Adding variants requires updating both matches and tests.

## Test Signals
A complete table-driven unit test verifies round trips for every listed variant. Additional tests reject unknown/gap values and confirm the default `StorageResult` error type.
