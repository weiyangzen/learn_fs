<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs

## Purpose
Implements a low-level blockstore decorator that encrypts data before storage and decrypts/authenticates data on load.

## APIs, Flow, And State
`EncryptedBlockStore<C, _B, B>` owns an underlying async-drop store, an `Arc<C>` cipher, and a shared global crypto thread pool. Reads delegate metadata and `exists`; `load` fetches ciphertext, verifies/removes a two-byte `FORMAT_VERSION_HEADER`, then decrypts. `overhead` adds the header plus cipher prefix/suffix overhead to the underlying store's overhead. Optimized writes allocate enough underlying prefix/suffix space, shrink the exposed mutable region to plaintext, then encrypt, prepend the header, and forward underlying optimized writes. `remove` and async drop delegate.

## Dependencies And Integration
Uses `cryfs_crypto::symmetric::CipherDef`, `LazyReclaim<ThreadPool>`, `Data` region growth/shrink APIs, and low-level blockstore reader/deleter/optimized-writer traits. Generic tests instantiate AES-256-GCM, AES-128-GCM, and XChaCha20-Poly1305 over `InMemoryBlockStore`.

## Risks And Test Signals
The header is encoded with `u16::to_ne_bytes`, so it is native-endian and should not be changed lightly for cross-platform persistence. `_check_and_remove_header` slices `data[..FORMAT_VERSION_HEADER.len()]` in the error path, so too-short data can panic rather than return a clean parse error. Tests cover generic low-level behavior, overhead calculations, successful same-key load, wrong-key failure, and tamper failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs -->
