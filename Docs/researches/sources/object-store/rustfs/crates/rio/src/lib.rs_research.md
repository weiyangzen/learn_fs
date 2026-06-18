<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/lib.rs -->
# sources/object-store/rustfs/crates/rio/src/lib.rs

## Purpose
Defines the public surface and shared capability traits for the `rustfs-rio` crate. It re-exports reader/writer wrappers, checksum utilities, compression/encryption types, and dynamic reader abstractions used by object I/O.

## Important APIs, types, and functions
- Exports `LimitReader`, `EtagReader`, `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, `HardLimitReader`, `HashReader`, checksum APIs, `WarpReader`, `Writer`, `HttpReader`, `HttpWriter`, `Index`, and `TryGetIndex`.
- Defines `ReadStream`, `ReaderCapabilities`, `Reader`, and `DynReader`.
- Defines `EtagResolvable`, `resolve_etag_generic`, and `HashReaderDetector`.
- Provides delegation macros for wrapper capability forwarding.
- `boxed_reader` and `wrap_reader` convert typed readers to `DynReader`.

## Control flow
There is little runtime logic. The module graph is assembled, traits define default no-op capabilities, blanket impls turn compatible async readers into crate reader traits, and `Box<T>` implementations forward capability calls to boxed dynamic readers.

## State and persistence behavior
No persistent state is stored. The file defines compile-time composition rules that determine whether runtime wrappers can expose ETag, hash-reader, and compression-index information through arbitrary nesting.

## Dependencies and integration points
Depends on Tokio traits through `ReadStream`, local modules, and compression index types. The exported `DynReader` contract is used by `HashReader`, HTTP adapters, compression/encryption wrappers, and higher-level object store code that wants a single boxed async reader type with metadata capabilities.

## Risks and edge cases
The delegation macros are central: any new wrapper that forgets to use them can hide ETags, hash-reader mutation, or compression indexes from outer layers. `DEFAULT_ENCRYPTION_BLOCK_SIZE` is 1 MiB while `encrypt_reader.rs` uses an internal 8 KiB block constant, so callers should not assume this public constant controls the current encryption frame size.

## Test signals
`lib.rs` has no local tests, but `etag.rs`, `hash_reader.rs`, compression, encryption, and HTTP tests exercise the public exports and trait forwarding.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/lib.rs -->
