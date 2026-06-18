# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/mod.rs

Purpose: Top-level cloud integration module for automatic provider detection, metadata fetching, and static/dynamic IP range sources.

Important APIs: Declares private `detector`, public `metadata`, private `ranges`, and re-exports `detector::*`, `metadata::*`, and `ranges::*`.

Control flow and state: No runtime logic; it is the namespace boundary joining detection, metadata provider implementations, and standalone cloud range helpers.

Dependencies and integration: Re-exported by crate `lib.rs`, making cloud range and metadata types part of the public trusted-proxies API. The listed files integrate with unlisted `detector.rs` through the `CloudMetadataFetcher` trait and provider detection path.

Risks and tests: Public wildcard re-exports can obscure API ownership and increase accidental API surface. Integration tests under `tests/integration/cloud_tests.rs` verify that public detector and metadata fetcher imports compile and basic disabled detection works.
