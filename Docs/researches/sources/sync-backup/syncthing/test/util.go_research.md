# sources/sync-backup/syncthing/test/util.go

Purpose: shared Syncthing integration-test utilities for deterministic file generation, mutation, directory comparison, process startup, cleanup, timeout detection, and remote sync checks.

Important APIs/functions: generation helpers `generateFiles`, `generateFilesWithTime`, `generateOneFile`, `ReadRand`, `randomName`, and `infiniteReader`; mutation helper `alterFiles`; cleanup `removeAll`; comparison helpers `compareDirectories`, `directoryContents`, `mergeDirectoryContents`, `compareDirectoryContents`, `startWalker`, `sha256file`, and `fileInfo`; process helpers `startInstance`, `checkedStop`, `getTestName`, `isTimeout`, `symlinksSupported`, and `checkRemoteInSync`.

Control flow: file generation opens a seed file and repeats it through `infiniteReader`, creating randomized names, modes, sizes, and mtimes. Directory walking emits canonical `fileInfo` records through channels and hashes regular files. Comparison sorts or pairwise compares these records. Instance startup builds REST addresses and log names, starts `../bin/syncthing` with per-instance home directories, awaits startup, and pauses folders for controlled tests.

State/persistence: writes trees under caller-supplied dirs, changes modes and mtimes, deletes globbed paths, creates logs under `logs/`, and uses Syncthing homes `hN`. Randomness is seeded in `init()` for repeatability, with some tests explicitly reseeding.

Dependencies/integration: relies on Go stdlib filesystem APIs, `crypto/sha256`, Syncthing `build` platform flags, and `lib/rc` process/REST helpers. `checkRemoteInSync` uses remote device status from running instances.

Risks: `removeAll` expands globs and recursively chmods before deletion, so callers must pass constrained paths. `alterFiles` intentionally races against walking and ignores some disappeared paths. Directory comparison includes Unix mode and second-level mtimes, which may be platform-sensitive. `startWalker` closes shared channels, so `compareDirectories` assumes all walkers are consumed uniformly.

Test signals: generated trees are verified by SHA-256, size, mode, symlink target hash, and coarse mtime; process helpers fail tests immediately on startup/stop errors; remote sync helper returns explicit device/folder mismatch errors.
