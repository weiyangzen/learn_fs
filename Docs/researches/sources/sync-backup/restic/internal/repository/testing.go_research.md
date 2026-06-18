
# sources/sync-backup/restic/internal/repository/testing.go

Purpose: provides repository test helpers for creating, opening, and validating repositories across versions and backends.

Important APIs include `TestUseLowSecurityKDFParameters`, `TestBackend`, `TestRepositoryWithBackend`, `TestRepository`, `TestRepositoryWithVersion`, `TestFromFixture`, `TestOpenLocal`, `TestOpenBackend`, `TestAllVersions`, `BenchmarkAllVersions`, and `TestCheckRepo`. Helpers configure low-cost scrypt params, disable chunker polynomial validation for tests, initialize memory or local backends, open existing fixtures, and run checker passes over indexes and pack contents.

State and persistence are test-scoped repositories, optional `RESTIC_TEST_REPO` local directories, config/key files, and low-security global key params. Integration points include backend factories, retry/local/memory backends, repository initialization/opening, checker loading, and versioned test loops. Risks include global test configuration leaking across tests, leaving local test repositories for inspection, and tests depending on lowered KDF cost. This file is a key signal for how production APIs are expected to be assembled in tests.
