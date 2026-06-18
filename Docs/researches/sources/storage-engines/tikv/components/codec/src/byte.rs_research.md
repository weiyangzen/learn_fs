# sources/storage-engines/tikv/components/codec/src/byte.rs

## Purpose
Implements byte-slice codecs used by TiKV binary keys and metadata streams. It has two families: memory-comparable bytes, where encoded byte order preserves or reverses lexical order, and compact bytes, where bytes are prefixed by a varint length and are not order preserving.

## APIs and control flow
`MemComparableByteCodec` encodes source bytes into 8-byte groups followed by a marker byte. Full groups use marker `0xff`; the terminal group is padded with zero bytes and marker `!(padding_size)`. Descending order reuses ascending encoding and bit-flips the encoded region. The main public methods are `encoded_len`, `get_first_encoded_len`, `get_first_encoded_len_desc`, `encode_all`, `encode_all_in_place`, descending variants, and `try_decode_first` variants. Decoding copies each data group, interprets the marker through `Ascending` or `Descending`, validates terminal padding with `libc::memcmp`, and returns read and written byte counts. `MemComparableByteEncoder` and `MemComparableByteDecoder` extend `NumberEncoder` and `BufferReader`.

`CompactByteCodec::get_first_encoded_len` inspects the leading varint length. `CompactByteEncoder` writes varint length plus raw bytes for `NumberEncoder` implementors and `std::fs::File`; `CompactByteDecoder` reads from `NumberDecoder` implementors and from `BufReader<T>`.

## State, dependencies, and integration
The production codec is stateless but mutates caller buffers and cursor positions. It depends on crate `buffer`, `number`, `ErrorInner`, `libc`, `std::io::Read`, and nightly `std::intrinsics::unlikely`. Integration is through the codec prelude and downstream key encoders that need bytewise sort compatibility.

## Risks and test signals
Unsafe pointer copies require non-overlap for out-of-place encoding and destination capacity at least `encoded_len`. Decoders can leave partial junk beyond `written_bytes`; callers must truncate. Compact length casts `i64` varints to `usize`, so corrupt negative lengths would be dangerous if produced externally. Tests cover exact encodings, first-encoded-length detection, compact file IO, in-place flips, overlap-safe decode, invalid padding and EOF, panic conditions, ordering preservation, plus benchmark-only comparisons against older implementations.
