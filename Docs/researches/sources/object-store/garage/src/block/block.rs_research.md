# sources/object-store/garage/src/block/block.rs

Purpose: defines the in-memory/path/stream representation of a Garage data block, including whether bytes are stored plain or zstd-compressed.

Important APIs/types/functions: `DataBlockHeader::{Plain, Compressed}`, generic `DataBlockElem<T>`, aliases `DataBlock`, `DataBlockPath`, and `DataBlockStream`, constructors `from_parts`, `plain`, `compressed`, accessors `into_parts` and `as_parts_ref`, `DataBlockHeader::is_compressed`, `DataBlock::verify`, `DataBlock::from_buffer`, and `zstd_encode`.

Control flow: `from_buffer` offloads optional compression to `tokio::task::spawn_blocking`; on successful zstd compression it returns a compressed block, otherwise it silently falls back to plain data. `verify` hashes plain bytes with `blake2sum`, while compressed blocks are validated by zstd decode into `sink` using the included checksum.

State and persistence: no persistence by itself, but `DataBlockHeader` drives on-disk extension choice and RPC stream metadata. The checksum-enabled `zstd_encode` affects long-term compatibility of compressed block files.

Dependencies and integration points: uses `bytes::Bytes`, `garage_util::data::Hash` and `blake2sum`, `garage_util::error::Error`, `garage_net::stream::ByteStream`, and `zstd`. Integrated by `manager.rs` for local writes, reads, RPC put/get, corruption detection, and compression policy.

Risks: compressed verification checks zstd integrity but not that decoded bytes hash to the requested block hash; this relies on the compressed frame checksum and immutable hash naming model. Compression failure fallback changes storage format without surfacing a warning. `spawn_blocking(...).await.unwrap()` will panic if the blocking task is cancelled/panics.

Test signals: no local unit tests in this file; covered indirectly by block IO, resync, and S3 object integration tests that write and read blocks.
