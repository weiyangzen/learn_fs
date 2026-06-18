# sources/object-store/rustfs/crates/signer/src/lib.rs

## Purpose
Crate root and public facade for request signing modules.

## Important APIs
It declares modules for constants, streaming SigV4, unsigned streaming trailer, SigV2, SigV4, and utilities. It re-exports `streaming_sign_v4`, `try_streaming_sign_v4`, SigV2 and SigV4 error types, legacy signing/presigning wrappers, and fallible `try_` variants including trailer signing.

## Control Flow and Integration
No runtime logic executes here. It stabilizes the public API so downstream ECStore clients and transition code can import signing functions from `rustfs_signer` directly.

## Risks and Test Signals
Any change to re-exports affects downstream compatibility. The crate root does not re-export `streaming_unsigned_v4`, so that remains module-addressed/internal. Tests are in implementation modules.
