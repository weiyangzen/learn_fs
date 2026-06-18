<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/reader.rs -->
# sources/object-store/rustfs/crates/rio/src/reader.rs

## Purpose
Defines `WarpReader`, a minimal adapter that turns any plain `AsyncRead + Unpin + Send + Sync` into a reader participating in `rio` capability traits.

## Important APIs, types, and functions
- `WarpReader<R>` stores `inner`.
- `WarpReader::new` constructs the adapter.
- `AsyncRead::poll_read` forwards directly to `inner`.
- Empty implementations of `HashReaderDetector`, `EtagResolvable`, and `TryGetIndex` mark the wrapped stream as capability-compatible but with no special metadata.

## Control flow
The read path is a single delegation to `Pin::new(&mut inner).poll_read(cx, buf)`. Capability calls use default trait behavior from `lib.rs`.

## State and persistence behavior
No state is added beyond ownership of the inner reader. It does not persist data or metadata and does not transform bytes.

## Dependencies and integration points
Depends on Tokio `AsyncRead`, local `TryGetIndex`, `EtagResolvable`, and `HashReaderDetector`. `wrap_reader` and `HashReader::from_stream` use `WarpReader` to bring ordinary readers into the `DynReader` ecosystem.

## Risks and edge cases
`WarpReader` intentionally hides any capabilities the original concrete type might have unless that type is wrapped through a more specific path. It requires `Unpin + Send + Sync`, matching the crate's dynamic reader contract.

## Test signals
There are no local tests. Indirect coverage comes from `HashReader::from_stream`, boxed reader capability tests, and all higher-level wrappers that accept plain `Cursor` or `BufReader` inputs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/reader.rs -->
