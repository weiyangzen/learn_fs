# sources/storage-engines/tikv/components/codec/src/buffer.rs

## Purpose
Defines low-level sequential memory buffer read/write traits used by the codec crate. It abstracts over `std::io::Cursor`, byte slices, mutable slices, boxed/delegated buffers, and growable `Vec<u8>` while exposing fast unsafe write access for encoders.

## Important APIs, Types, And Functions
- `BufferReader` exposes `bytes`, `advance`, and `read_bytes`.
- `BufferReader` implementations exist for `Cursor<T: AsRef<[u8]>>`, `&[u8]`, `&mut T`, and `Box<T>`.
- `BufferWriter` exposes unsafe `bytes_mut`, unsafe `advance_mut`, and safe `write_bytes`.
- `BufferWriter` implementations exist for `Cursor<T: AsMut<[u8]>>`, `&mut [u8]`, `Vec<u8>`, `&mut T`, and `Box<T>`.
- Error paths use `ErrorInner::eof().into()` when fixed-size buffers cannot satisfy reads/writes.

## Control Flow
Readers expose remaining buffer, advance cursors/slices, and return borrowed slices when enough bytes are present. Writers expose writable memory and require callers to advance only after initialization. Fixed-size writers fail on insufficient space; `Vec<u8>` reserves capacity and extends length via unsafe `set_len`.

## State And Persistence Behavior
State is current cursor position, slice start pointer, or `Vec` length/capacity. No external persistence exists. The traits intentionally mutate internal position to support sequential encoding/decoding.

## Dependencies And Integration Points
Depends on crate `ErrorInner`/`Result` and nightly `std::intrinsics::unlikely` for branch hints. Higher-level codec modules use these traits to encode/decode bytes and numbers efficiently.

## Risks And Edge Cases
Cursor `read_bytes` and `write_bytes` use `pos + count >= slice.len()` / `pos + write_len >= slice.len()`, so exact-to-end non-zero reads/writes fail; this may be historical behavior or an off-by-one risk. Unsafe `bytes_mut`/`advance_mut` can expose or commit uninitialized memory. Slice advances can panic on over-advance. The ignored reallocation test documents uncertain reliance on allocator-specific `Vec::reserve` behavior for bytes written past length before `advance_mut`.

## Test Signals
Tests cover cursor and slice readers, cursor/slice/Vec writers, zero-length operations, invalid cursor positions, and insufficient fixed-size writes. Ignored `test_vec_reallocate` records unresolved reliance on unspecified `Vec` reallocation behavior.
