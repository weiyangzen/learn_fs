# sources/security-integrity/cryfs/crates/utils/src/path/error.rs

Purpose: shared parse error enum for path and path-component validation.

Important APIs/types/functions: `ParsePathError` variants: `NotAbsolute`, `EmptyComponent`, `NotUtf8`, and `InvalidFormat`; derives `Debug`, `Error`, `PartialEq`, and `Eq`.

Control flow/state: no runtime logic beyond formatting errors via `thiserror`.

Dependencies/integration: consumed by `PathComponent`, `PathComponentBuf`, and likely `AbsolutePath` parsing.

Risks: small variant set may collapse distinct invalid cases, limiting diagnostics. `NotAbsolute` is also used for `.`/`..` components.

Test signals: asserted throughout component and iterator/path tests.
