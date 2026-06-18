<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/writer.rs -->
# sources/object-store/rustfs/crates/rio/src/writer.rs

## Purpose
Provides a small dynamic `AsyncWrite` enum for writing to memory, HTTP streams, or arbitrary boxed async writers through one type.

## Important APIs, types, and functions
- `Writer::Cursor`, `Writer::Http`, and `Writer::Other` variants.
- Constructors `from_tokio_writer`, `from_cursor`, and `from_http`.
- Accessors and consuming extractors for cursor and HTTP variants.
- `AsyncWrite` implementation delegates write, flush, and shutdown to the selected variant.

## Control flow
Construction boxes HTTP and arbitrary writers as needed. Runtime write operations pattern-match on the enum variant and pin-project the contained writer with `Pin::new`, then call the corresponding async write method.

## State and persistence behavior
`Cursor` stores bytes in memory and can be extracted with `into_cursor_inner`. `Http` writes are persisted only by the remote HTTP endpoint. `Other` delegates persistence semantics to the supplied writer.

## Dependencies and integration points
Depends on Tokio `AsyncWrite`, `std::io::Cursor`, and local `HttpWriter`. It is the output-side companion to `DynReader` for code that needs a single write target type.

## Risks and edge cases
The enum is `Unpin` only because its variants are compatible with `Pin::new` usage here; adding a non-`Unpin` writer would require a different projection strategy. Extractor methods consume or borrow only matching variants and silently return `None` otherwise.

## Test signals
There are no local tests. HTTP writer behavior is tested in `http_reader.rs`; cursor behavior relies on Tokio's `AsyncWrite` implementation for `Cursor<Vec<u8>>`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/writer.rs -->
