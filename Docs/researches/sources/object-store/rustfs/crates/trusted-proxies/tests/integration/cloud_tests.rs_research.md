# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/cloud_tests.rs

Purpose: Minimal async integration coverage for cloud provider detection/metadata exports.

Important APIs tested: `CloudDetector::new(false, timeout, None).detect_provider()` and `AwsMetadataFetcher::new(...).provider_name()`.

Control flow: Disabled detector should return `None` without external metadata calls. AWS metadata fetcher construction should expose provider name `aws`.

State and dependencies: Uses Tokio tests and imports public crate APIs. No persistent state.

Integration points: Confirms crate-level public re-exports for `CloudDetector`, `AwsMetadataFetcher`, and `CloudMetadataFetcher`.

Risks and coverage gaps: Does not test enabled detection, GCP/Azure fetchers, network CIDR parsing, public range fetches, or failure fallback behavior. It intentionally avoids real cloud metadata/network dependency.
