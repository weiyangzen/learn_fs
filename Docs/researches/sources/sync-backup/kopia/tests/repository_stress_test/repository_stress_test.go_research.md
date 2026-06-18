
# sources/sync-backup/kopia/tests/repository_stress_test/repository_stress_test.go

## Purpose
Runs randomized concurrent repository stress tests over direct repository APIs, mixing content writes/reads, manifest writes/reads, listing, flush, refresh, and compaction across multiple configs, open repositories, sessions, and workers.

## Important APIs, Types, And Functions
- `StressOptions` controls number of configs/open repositories/sessions/workers and action weights.
- Test entry points `TestStressRepositoryMixAll`, `TestStressRepositoryRandomMix`, `TestStressRepositoryManifests`, `TestStressContentWriteHeavy`, and `TestStressContentReadHeavy` configure weighted scenarios.
- `runStress` gates on `KOPIA_STRESS_TEST`, initializes filesystem storage/repository, creates multiple config/cache files, starts worker goroutines, and runs for 10 or 120 seconds depending on CI context.
- `longLivedRepositoryTest` opens a repository, creates direct writers per session, and starts worker loops.
- `repositoryTest` roulette-selects actions until stopped.
- Actions implement random content write/read, list/read all, compact indexes, flush, refresh, read/write manifests.

## Control Flow
The harness creates one physical repository and multiple connected configs. For each config/open/session/worker, goroutines execute random actions. The in-memory `repomodel` tracks which content/manifests should be visible pending flush, after flush, or after refresh. Errors other than `errSkipped` fail the worker and test.

## State And Persistence Behavior
Mutates a real filesystem-backed repository, config files, cache directories, worker logs, content blobs, index blobs, and manifest metadata. The model state tracks expected visibility transitions for content and manifests.

## Dependencies And Integration Points
Uses low-level `repo` APIs, `repo.DirectRepositoryWriter`, `content`, `manifest`, `indexblob`, filesystem storage, `errgroup`, `testlogging`, `testutil`, and the `repomodel` package.

## Risks And Edge Cases
Random map iteration plus random weights can make failures hard to reproduce. The test is skipped unless `KOPIA_STRESS_TEST` is set and can run longer in non-PR CI. It assumes model semantics match repository consistency semantics; model bugs can mask or invent failures. Shared log file writes from multiple goroutines are not explicitly synchronized.

## Test Signals
Strong concurrency and consistency signal for direct repository writers, flush/refresh visibility, index compaction, and manifest/content read paths.
