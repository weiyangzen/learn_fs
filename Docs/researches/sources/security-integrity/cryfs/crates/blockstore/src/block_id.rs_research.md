<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs

## Purpose
Defines the 16-byte `BlockId` type used as the stable identifier for blocks and blob roots.

## APIs, Flow, And State
`BlockId` wraps `[u8; BLOCKID_LEN]` and derives copy/clone/equality/hash/order traits. Constructors include random generation via `rand::rng().fill`, `zero`, `from_slice`, `from_array`, and `from_hex`; accessors/formatters include `data`, `to_hex`, `to_hex_upper`, `Display`, and `Debug`. `BinRead` and `BinWrite` serialize exactly the 16-byte array.

## Dependencies And Integration
Used throughout high-level and low-level blockstores, blob IDs, integrity errors, and streams. Binary serialization integrates with `binrw` and utility test helpers.

## Risks And Test Signals
`from_slice` fails on non-16-byte inputs via `try_into`. Random collision probability is assumed low but not impossible; `LockingBlockStore::create` still retries on `try_create` collision. Tests cover binary round-trip, display hex, and debug format.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs -->
