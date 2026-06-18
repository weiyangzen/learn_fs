# sources/user-network-fs/rclone/backend/b2/b2_internal_test.go

## Purpose
B2-specific internal integration tests for behavior not fully covered by generic fstests: Backblaze URL encoding, millisecond modtime metadata, direct and large upload metadata, versions, point-in-time views, cleanup, unfinished uploads, and lifecycle rules.

## Important APIs, types, and functions
`encodeTest` and `TestUrlEncode` validate B2 native string encoding. `TestTimeString` and `TestParseTimeString` cover `src_last_modified_millis` conversion. `internalTestMetadata` uploads randomized data with MIME type, metadata, and B2 info headers under configurable size/cutoff/chunk settings. `InternalTestVersions` creates old/current/deleted versions and checks `Versions`, version suffixes, `VersionAt`, dry-run cleanup, and real cleanup. `InternalTestCleanupUnfinished` creates unfinished large uploads with `newLargeUpload`. `InternalTestLifecycleRules` exercises lifecycle backend command reads, dry-runs, and updates.

## Control flow
Tests run against a real B2 remote. They mutate backend options to force direct or multipart paths, use sleeps to separate B2 timestamps, create/delete/recreate objects to generate versions, and compare listings before and after cleanup. `InternalTest` registers all subtests for the fstests internal tester hook.

## State and persistence
The tests create remote B2 objects, hidden versions, unfinished large-file markers, and lifecycle rules. They also mutate in-memory `f.opt.Versions`, `f.opt.VersionAt`, upload chunk size, and upload cutoff, with defers where needed.

## Dependencies and integration points
Uses `fstest`, `fstests`, `fs/cache`, B2 `api`, `bucket`, `version`, rclone `object`, random data generation, and testify assertions. It is in package `b2` to access unexported helpers and state.

## Risks
Timing-sensitive version tests depend on sleeps and remote timestamp behavior. Lifecycle tests assume a clean initial lifecycle state. Cleanup tests are intentionally destructive and need isolated integration paths. Metadata coverage is limited to current backend metadata support, mostly `mtime`.

## Test signals
Strong direct signal for B2-specific encoding, metadata, versioning, point-in-time listing, cleanup, unfinished upload cleanup, and lifecycle command behavior. Interface assertion confirms `*Fs` implements `fstests.InternalTester`.
