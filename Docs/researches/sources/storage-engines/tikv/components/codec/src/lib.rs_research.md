# sources/storage-engines/tikv/components/codec/src/lib.rs

## Purpose
Crate root for TiKV's low-level codec component. It exposes buffer, byte, and number codecs plus the common error type and prelude.

## APIs and control flow
The root enables nightly features needed by child modules: `test` under cfg(test), `core_intrinsics`, and `min_specialization`. It imports `tikv_alloc`, declares public modules `buffer`, `byte`, and `number`, keeps `convert` and `error` private, and exports `Error`, `ErrorInner`, and `Result`.

The `prelude` re-exports `BufferReader`, `BufferWriter`, byte encoder and decoder traits, compact-byte traits, and number encoder and decoder traits. Downstream code can import the prelude to gain extension methods on buffers and cursors.

## State, dependencies, and integration
This file owns no runtime state. Its integration role is API shaping: it hides conversion internals but exposes codec extension traits. `tikv_alloc` is retained as an extern crate for allocator integration even if not referenced directly here.

## Risks and test signals
The crate is tied to nightly Rust features. Any downstream module expecting the prelude depends on these exact re-export names. There are no direct tests in this file; child module tests validate that the exposed traits work for `Vec`, slices, cursors, and file readers.
