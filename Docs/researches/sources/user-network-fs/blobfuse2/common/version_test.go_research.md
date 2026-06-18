# sources/user-network-fs/blobfuse2/common/version_test.go
## sources/user-network-fs/blobfuse2/common/version_test.go

Purpose: validates `Version.compare` ordering for stable and prerelease version strings.

Important APIs/helpers: `versionTestSuite`, `TestVersionEquality`, `TestVersionSuperiority`, `TestVersionInferiority`, and `TestVersionTestSuite`.

Control flow: tests parse pairs of version strings and assert raw `compare` results. Equality covers identical stable, preview, beta, and tilde-preview forms. Superiority covers greater major/minor/patch, GA greater than preview, higher preview numeric suffix, and tilde/dash preview comparisons. Inferiority covers the inverse cases.

State and persistence: no external state or files.

Dependencies/integration: testify suite/assert and `ParseVersion`.

Risks: tests ignore parse errors by discarding them, so a future parser failure could lead to nil dereference rather than a clear parse assertion. They do not cover invalid strings, `OlderThan`, `NewerThan`, or `String` directly. Comparisons between different prerelease labels with the same numeric segment are not tested.

Test signals: confirms intended ordering semantics used by command version checking and release warnings.
