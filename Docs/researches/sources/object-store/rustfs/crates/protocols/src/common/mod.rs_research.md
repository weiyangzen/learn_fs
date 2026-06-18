# sources/object-store/rustfs/crates/protocols/src/common/mod.rs

Purpose: This is the common module facade for protocol-independent pieces: storage client traits, authorization gateway, session identity, and the test-only dummy backend.

Important APIs and types: It declares `client`, `gateway`, and `session`, plus `dummy_storage` under `cfg(test)`. It re-exports `S3StorageBackend`, `AuthorizationError`, `S3Action`, `authorize_operation`, `is_operation_supported`, `ProtocolPrincipal`, and `SessionContext`.

Control flow: There is no runtime control flow beyond Rust module resolution and re-export selection. Test builds include `dummy_storage`; non-test builds exclude it.

State and persistence behavior: This file owns no state. It controls visibility of shared APIs and keeps the production module graph free of the dummy backend.

Dependencies and integration points: `lib.rs`, FTPS, SFTP, Swift, and WebDAV consumers use this facade to avoid depending on deeper module paths. The `S3StorageBackend` alias is especially important for protocol drivers that are generic over the object-store backend.

Risks: Re-export changes are public API changes for the protocols crate. Accidentally exposing test-only helpers outside `cfg(test)` would increase production surface area.

Test signals: The main signal is compilation of downstream modules and tests that import from `crate::common`. There are no direct tests in this file.
