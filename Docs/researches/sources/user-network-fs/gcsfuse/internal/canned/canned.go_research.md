<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/canned/canned.go -->
# Research: sources/user-network-fs/gcsfuse/internal/canned/canned.go

Purpose: supplies a small fake GCS bucket with deterministic canned contents for tests and examples.

Important APIs/types/functions: constants `FakeBucketName`, `TopLevelFile`, `TopLevelFile_Contents`, `TopLevelDir`, `TopLevelDir_Contents`, `ExplicitDirFile`, `ExplicitDirFile_Contents`, `ImplicitDirFile`, `ImplicitDirFile_Contents`, and function `MakeFakeBucket`.

Control flow: `MakeFakeBucket` constructs a `fake.NewFakeBucket` with `timeutil.RealClock`, the intentionally invalid bucket name `fake@bucket`, and default `gcs.BucketType`. It then iterates over a map of object names to contents and creates each object with `CreateObject`. Any creation failure panics via `log.Panicf`, which is appropriate for fixture setup.

State and persistence: state is an in-memory fake bucket only. Contents include a top-level file, an explicit directory placeholder object, a file inside that explicit directory, and a file that implies a directory prefix without a placeholder.

Dependencies and integration points: depends on `internal/storage/fake`, `internal/storage/gcs`, `strings`, `timeutil`, and `context`. It is intended as helper code for tests that need standard object/directory layouts.

Risks: uses a Go map for setup ordering, but ordering should not matter because objects are independent. Panicking on setup error is convenient for tests but unsuitable for production. The bucket name is intentionally not a valid real GCS bucket name, preventing accidental use against real storage.

Test signals: no direct tests in this subset, but downstream filesystem tests use fake buckets with similar object layouts to validate explicit and implicit directory semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/canned/canned.go -->
