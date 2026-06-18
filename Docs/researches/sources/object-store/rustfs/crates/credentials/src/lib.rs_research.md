<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/lib.rs -->
# sources/object-store/rustfs/crates/credentials/src/lib.rs

## Purpose
Crate root for `rustfs-credentials`, exposing constants and credential APIs while keeping the datetime serde helper internal.

## Important APIs, types, and functions
Declares modules `constants`, `credentials`, and `serde_datetime`; publicly re-exports `constants::*` and `credentials::*`.

## Control flow
No runtime flow; module declarations determine public API visibility.

## State and persistence behavior
No state directly, though the re-exported credentials module contains process-global OnceLocks.

## Dependencies and integration points
Used by RustFS crates importing credential constants, generators, global credential accessors, and `Credentials`.

## Risks and edge cases
The datetime module is private, so external callers rely on `Credentials` serde behavior rather than direct helper access. Re-export changes are public API breaks.

## Test signals
Compilation and public API import tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/lib.rs -->
