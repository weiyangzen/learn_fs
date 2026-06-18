# sources/storage-engines/tikv/deny.toml

## Purpose
Configures `cargo-deny` policy for TiKV dependencies, with emphasis on FIPS-oriented crypto restrictions, advisory handling, allowed licenses, and trusted source origins.

## Important APIs, Types, and Functions
The `[bans]` section denies RustCrypto/hash/TLS/signature-related crates while allowing explicit wrapper paths for cloud SDKs, checksums, and runtime FIPS providers. `[advisories]` denies yanked crates, tracks unmaintained advisories at workspace scope, and documents specific ignored RustSec IDs. `[licenses]` allows Apache-compatible and approved permissive licenses with explicit exceptions. `[sources]` denies unknown registries/git sources and allows selected GitHub orgs.

## Control Flow
This file is declarative. `cargo deny` traverses the resolved dependency graph, applies wrapper exceptions to banned crates, evaluates RustSec advisory policy, checks license expressions and exceptions, then validates source provenance.

## State and Persistence Behavior
No runtime state. It is a persisted CI/security policy and should evolve with dependency updates, RustSec advisories, and legal/security decisions.

## Dependencies and Integration Points
Used by dependency-audit CI and local security checks. It integrates indirectly with the Cargo workspace lockfile and any dependency introduced by TiKV crates, cloud storage integrations, TLS clients, and OpenSSL bindings.

## Risks
Ignored advisories are intentional risk acceptances and require active review; several are tied to avoiding OpenSSL 3.x performance regressions. Wrapper exceptions can mask newly introduced crypto use if dependency paths change. The policy allows multiple versions, so supply-chain risk is controlled by bans/advisories rather than deduplication.

## Test Signals
Run `cargo deny check` after dependency changes. Review failures when adding cloud SDK, TLS, crypto, checksum, or license-sensitive crates. Periodically revalidate ignored RustSec entries and wrapper paths against the current dependency graph.
