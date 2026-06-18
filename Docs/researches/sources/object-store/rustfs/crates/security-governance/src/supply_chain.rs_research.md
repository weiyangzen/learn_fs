# sources/object-store/rustfs/crates/security-governance/src/supply_chain.rs

## Purpose
Models supply-chain integrity requirements for build artifacts, third-party downloads, and generated release assets. It validates that artifact metadata requires digests, provenance, and signatures where appropriate.

## Important APIs and Types
`ArtifactSourceKind` is `WorkspaceBuild`, `ThirdPartyDownload`, or `GeneratedReleaseAsset`. Its helper methods require digest for third-party and generated assets, and provenance/signature for generated release assets. `ArtifactIntegrityPolicy` stores artifact name, source kind, and booleans for digest/signature/provenance requirements with const constructor/getters. `SupplyChainPolicyError` reports empty artifact names, missing digest/provenance/signature requirements, and duplicate artifact policies.

`validate_artifact_integrity_policies` scans policies, rejects empty artifacts, applies source-derived requirements, and uses a `BTreeSet<&'static str>` for artifact uniqueness.

## Control Flow and State
Validation is synchronous and stateless. It returns the first policy violation and does not inspect files, signatures, provenance documents, or actual release assets.

## Integration Points
Re-exported by the crate root, the policy can feed release validation, CI policy checks, or admin/reporting surfaces that describe artifact trust requirements.

## Risks
The model verifies declared requirements, not the presence or cryptographic validity of artifacts. Workspace builds may omit digest/provenance while still setting signature required, which may or may not match release policy. Artifact identity is exact and static.

## Test Signals
Unit tests cover valid workspace/generated policies, empty artifacts, missing digest for third-party and generated assets, missing provenance/signature for generated assets, and duplicate artifact rejection.
