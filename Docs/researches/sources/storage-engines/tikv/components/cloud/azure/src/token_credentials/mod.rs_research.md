# sources/storage-engines/tikv/components/cloud/azure/src/token_credentials/mod.rs

## Purpose
Declares the Azure token credential submodule.

## Important APIs, Types, And Functions
- `pub mod certificate_credentials;` makes `certificate_credentials.rs` available to the crate and public re-exports in `lib.rs`.

## Control Flow
No runtime logic is present.

## State And Persistence Behavior
No state is held here.

## Dependencies And Integration Points
This module boundary lets `crate::ClientCertificateCredentialExt` be exported from the crate root and used by Azure KMS.

## Risks And Edge Cases
The module currently exposes only certificate credentials; additional credential types should be added deliberately to avoid confusing Azure SDK built-ins with local extensions.

## Test Signals
No direct tests.
