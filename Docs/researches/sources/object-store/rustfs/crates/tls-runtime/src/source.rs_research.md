## sources/object-store/rustfs/crates/tls-runtime/src/source.rs

Purpose: models where TLS material is loaded from and the expected filenames/layout inside a TLS directory.

Important APIs/types/functions: `TlsSourceKind::{Directory, ExplicitFiles}` reserves source strategies; current constructor is `TlsSource::from_directory`. `TlsFileLayout` names server cert/key, public CA, client CA, client cert, and client key filenames using `rustfs_config` constants by default. `TlsSource` stores kind, base directory, layout, fallback CA filename, trust flags, and server mTLS enablement. `validate_directory` rejects empty, missing, and non-directory paths.

Control flow and state: construction sets directory mode, default filenames, fallback CA as `RUSTFS_CA_CERT`, and trust/mTLS flags false. Validation only checks filesystem path shape; it does not inspect files.

Dependencies and integration points: consumed by material loading, coordinator status, and reloadable server resolver. It is the root of all shared TLS runtime file discovery.

Risks: `ExplicitFiles` is declared but no constructor/validation behavior exists here, so callers should not assume explicit-file mode is implemented. Trust flags are stored but not acted on in the visible material loading path. Validation uses live filesystem checks.

Test signals: crate-level test verifies missing directory produces `TlsRuntimeError::DirectoryNotFound`.
