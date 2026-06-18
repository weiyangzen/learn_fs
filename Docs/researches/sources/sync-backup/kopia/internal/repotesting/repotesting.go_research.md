# sources/sync-backup/kopia/internal/repotesting/repotesting.go

Purpose: provides a high-level test environment for creating, opening, reopening, and inspecting Kopia repositories.

Important APIs/types/functions: `Environment`, `Options`, `RepositoryMetrics`, `RootStorage`, `setup`, `Close`, `ConfigFile`, `MustReopen`, `MustOpenAnother`, `MustConnectOpenAnother`, `VerifyBlobCount`, `LocalPathSourceInfo`, `repoOptions`, `NewEnvironment`, `DefaultPasswordForTesting`, and `FormatNotImportant`.

Control flow: setup creates temp config/storage, initializes a repository at a requested format, opens it with test client options and optional time/metrics hooks, and exposes helpers for reopening or opening additional connections. Close shuts down repository and storage resources.

State and persistence behavior: test repository state persists in temp directories or in-memory blob storage for the test lifetime; environment records config file, storage, repository writer, metrics, and injected time.

Dependencies and integration points: heavily used by server, repo, snapshot, and maintenance tests.

Risks and test signals: helpers call `require`/`Fatal` style APIs and are unsuitable for production code; tests should close environments and validate blob counts after operations.
