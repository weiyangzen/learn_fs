# sources/user-network-fs/blobfuse2/common/version.go
## sources/user-network-fs/blobfuse2/common/version.go

Purpose: parses and compares blobfuse2 version strings and defines release metadata URLs for warning/block/latest checks.

Important APIs/types/functions: `BlobFuse2WarningsURL`, `BlobFuse2BlockingURL`, `GitHubReleaseBaseURL`, `Version`, `ParseVersion`, `compare`, `OlderThan`, `NewerThan`, and `String`.

Control flow: `ParseVersion` accepts three-segment stable versions or four raw dot segments when the third segment includes `-` or `~` preview marker. It stores four numeric segments, marks preview versions, strips the prerelease marker from the patch segment, and parses numeric pieces. `compare` short-circuits identical original strings, compares major/minor/patch numerically, then treats GA as newer than preview and compares preview numeric segment when both are previews.

State and persistence: no mutable state in this file. Constants feed root version checks.

Dependencies/integration: used by `cmd/root.go` before version metadata checks and by tests. Release constants point to raw GitHub benchmark-branch sentinel files and aka.ms warning/blocking pages.

Risks: parser only models a subset of semantic versioning. Preview type names such as beta/alpha are ignored; different prerelease labels with the same numeric suffix can compare equal. The four-segment acceptance condition is tied to dots and marker placement. Comments still include a TODO about preview-vs-GA, although the code handles that case.

Test signals: `version_test.go` covers equality, superiority, and inferiority for stable, `-preview`, `~preview`, and beta-like strings.
