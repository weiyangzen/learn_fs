
# sources/sync-backup/kopia/tests/endurance_test/endurance_test.go

## Purpose
Runs a long randomized endurance scenario against a WebDAV repository with fake time, multiple independent runners, concurrent snapshot/verify/maintenance actions, and clock jumps simulating two weeks of operation.

## Important APIs, Types, And Functions
- `webdavDirWithFakeClock` wraps `webdav.Dir` and adjusts write mtimes to fake server time.
- `TestEndurance` starts a fake time HTTP server, a WebDAV server, creates a WebDAV repo, and launches three parallel runners.
- `runnerState`, `action`, `actionInfo`, and `actions` define weighted operations.
- Action functions snapshot existing sources, snapshot all, verify snapshots/content, run maintenance, jump fake clock, add sources, and mutate directory trees.
- `pickRandomEnduranceTestAction`, `enduranceRunner`, and `runOneIterationUsingLock` drive weighted randomized execution with shared locks for exclusive actions.

## Control Flow
The test initializes fake time at `2000-01-01` and advances until two simulated weeks pass. Each runner connects to the same WebDAV repo under a distinct username, adds at least one source, then repeatedly selects weighted actions. Exclusive actions acquire a write lock; non-exclusive actions acquire a read lock. Any runner failure increments `failureCount`, causing other runners to stop early.

## State And Persistence Behavior
Persists repository data in a temp WebDAV-backed filesystem, modifies source directories, advances fake repository/server time, writes snapshot manifests, content, and maintenance records. Runner-local source directory lists are kept in memory, while repository data is shared.

## Dependencies And Integration Points
Uses `faketime`, `testenv.FakeTimeServer`, `webdav`, `testdirtree`, CLI executable runner, fake clock env var `KOPIA_FAKE_CLOCK_ENDPOINT`, and WebDAV repository storage.

## Risks And Edge Cases
Randomized action selection and fake-time jumps make failures potentially non-reproducible unless logs are preserved. WebDAV file mtime manipulation relies on concrete `*os.File` returned by `webdav.Dir`. Test duration is potentially long because fake time advances via weighted actions, not wall-clock deadlines.

## Test Signals
Broad stress signal for repository consistency under time advancement, maintenance, concurrent clients, and repeated snapshot/verify operations.
