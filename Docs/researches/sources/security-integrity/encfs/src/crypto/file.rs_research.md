## sources/security-integrity/encfs/src/crypto/file.rs

Purpose: File-level encoder/decoder for encrypted EncFS file contents. It maps logical plaintext offsets to physical encrypted blocks, handles per-file headers, legacy MAC/AES-GCM-SIV block overhead, read-modify-write partial blocks, sparse-hole behavior, and logical/physical size conversion.

Important APIs and types: traits `ReadAt`, `WriteAt`, `FileLen`; `FileCodecParams`; `FileDecoder::new`, `new_with_mode`, `new_from_config`, `calculate_logical_size`, `calculate_logical_size_with_mode`, `read_at`; `FileEncoder::new`, `new_with_mode`, `new_from_config`, `calculate_physical_size`, `calculate_physical_size_with_mode`, `write_at`, and internal `write_at_internal`.

Control flow: Decoding builds `BlockLayout`/`BlockCodec`, then loops over logical blocks, reads physical blocks at `header_size + block_num * block_size`, decrypts, slices requested bytes, and stops on EOF. Encoding calculates current logical size from physical length; if writing past EOF it fills the gap with encrypted zero blocks, then splits user data across logical block boundaries. Partial writes read and decrypt existing blocks for read-modify-write unless a write overwrites the existing payload from block start; encrypted blocks are written with `write_at`.

State and persistence: Mutates encrypted file bytes and relies on file headers and block metadata chosen by config. Dependencies are `crypto/block`, `SslCipher`, Unix `FileExt`, and callers such as FUSE filesystem and fuzz target. Risks include complexity around partial blocks, holes, offset arithmetic, and authentication failures during RMW. Tests use a mock file to cover size conversion, no-MAC round trips, MAC modes, partial writes, and AES-GCM-SIV layout.
