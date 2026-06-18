# sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/mod.rs

Purpose: module facade for the low-level inode API.

Important APIs: declares `interface`, re-exports `ReplyXTimes` and the main reply structs, directory reply traits, add-result enum, and `AsyncFilesystemLL`.

Control flow and state: no runtime behavior.

Dependencies and integration: imported by object low-level adapter, backend adapters, and tests/mocks.

Risks and tests: re-export list defines the crate's low-level public API. Platform-gated `ReplyXTimes` use in implementations must match this module's public surface.
