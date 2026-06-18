# sources/security-integrity/cryfs/crates/rustfs/src/lib.rs

Purpose: crate root and public API assembly for RustFS.

Important APIs: public modules `object_based_api`, `high_level_api`, `low_level_api`, and feature-gated `backend`; public re-exports of common types, `Data`, and callback helpers. Test module is enabled under `cfg(test)`.

Control flow and state: no runtime behavior. Feature flags determine whether backend and handle-related public items are available.

Dependencies and integration: users implement object or high/low-level traits through the exported types. `cryfs_utils::data::Data` is exposed for open-file data transfer.

Risks and tests: crate surface is feature-sensitive. Public re-exports make internal common type changes semver relevant.
