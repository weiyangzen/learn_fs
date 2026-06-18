# sources/security-integrity/cryfs/crates/check/src/error/display/mod.rs

Purpose: This module root exposes shared display utilities for concrete corruption errors.

Important APIs and flow: It declares `error_title`, `blob_error`, and `node_error` submodules and publicly reexports `ErrorTitle`, `BlobErrorDisplayMessage`, `ErrorDisplayBlobInfo`, `NodeErrorDisplayMessage`, and `ErrorDisplayNodeInfo`.

State and persistence: It has no state. It shapes the public-internal display API used by sibling error modules.

Dependencies and integration: Concrete error files import from `super::display` instead of reaching into individual display submodules.

Risks and test signals: This is a narrow facade. Renaming exports would affect every error `Display` implementation.
