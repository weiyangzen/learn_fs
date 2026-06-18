# sources/object-store/minio/cmd/erasure-healing-common_test.go

Purpose: Validates helper logic for selecting the latest metadata, common modtimes/parities, online disks, and disks needing part healing.

Important APIs/types/functions: Defines test-local `getLatestFileInfo` using quorum reduction and common modtime. `TestCommonTime` checks quorum time selection and sentinel fallback. `TestListOnlineDisks` and `TestListOnlineDisksSmallObjects` prepare erasure backends, tamper parts or inline metadata, then assert list/filter behavior. `TestDisksWithAllParts` covers healthy data, stale modtime, stale DataDir, and corrupted part checks. `TestCommonParities` validates parity choice when different `FileInfo` versions occur equally but only one parity has read quorum.

Control flow and state: Tests create temporary erasure backends, put objects, read/modify `FileInfo`, sometimes write metadata back, then call production helpers and verify disk filtering or part-healing flags. Several tests skip or adapt to platform constraints.

Dependencies and integration points: Exercises object-layer helpers (`prepareErasure16`, `PutObject`, `readAllFileInfo`), storage disk operations, `madmin.HealDeepScan`, metadata write helpers, and parity helpers defined elsewhere in the erasure metadata stack.

Risks: Tests use actual filesystem-backed storage fixtures and direct file corruption/removal; failures can be platform-sensitive. The local `getLatestFileInfo` mirrors production concepts but is not the production picker, so drift is possible.

Test signals: Strong evidence for metadata quorum and part verification behavior, including inline small-object coverage.
