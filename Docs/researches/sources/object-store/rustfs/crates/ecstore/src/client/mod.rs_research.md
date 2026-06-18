# sources/object-store/rustfs/crates/ecstore/src/client/mod.rs

## Purpose
Declares the `client` module surface for ecstore's S3/transition-client implementation.

## Important APIs, types, and functions
It publicly exposes modules for admin helpers, bucket policy, error response mapping, get/list/put APIs, multipart/streaming, remove/restore/stat APIs, bucket cache, checksum, constants, credentials, object utilities, common object handlers, signer errors, transition core, and header/base64 utilities.

## Control flow
There is no executable control flow. Compilation and visibility are the only effects: sibling modules become addressable as `crate::client::<module>`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
This is the integration point for all client submodules. Other crate areas import from this namespace to reach transition operations, object helpers, credentials, and error types.

## Risks and edge cases
Because every listed submodule is public, internal helper modules become part of the crate-visible API surface. Renaming or removing entries has broad compile impact.

## Test signals
No direct tests are meaningful beyond successful crate compilation and downstream module tests.
