# sources/test-tools/syzkaller/pkg/covermerger/provider_monorepo.go

Purpose: implements `FileVersProvider` using a local monorepo checkout/cache of kernel commits.

Important APIs/types/functions: `FileVersProvider`, `monoRepo`, `FileVersions`, `GetFileVersions`, `allRepoCommitsPresent`, `addRepoCommit`, `MakeMonoRepo`, and `cloneCommits`.

Control flow: `GetFileVersions` checks under read lock whether all requested commits are available; if not, it releases the read lock and calls `cloneCommits`. It then reads each requested file object from the local repo at the target commit, skipping missing files. `cloneCommits` checks whether commits already exist locally and otherwise checks them out/fetches via `addRepoCommit`.

State and persistence: persistent local VCS checkout under `<workdir>/repos/linux_kernels`; in-memory set of known repo commits protected by a mutex.

Dependencies and integration: uses syzkaller `vcs.NewRepo`, Linux target metadata, and logging. Used by batch/offline merge jobs needing many commit versions.

Risks: `addRepoCommit` records a commit as present before checkout success; failures can poison the cache for that run. It panics if repo or commit is empty. Concurrent clone behavior is protected but long checkouts block all cache updates.

Test signals: no direct tests in this subset; integration tests use a hand-written filesystem provider.
