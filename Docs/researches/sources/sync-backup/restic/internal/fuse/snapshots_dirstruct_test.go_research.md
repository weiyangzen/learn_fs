## sources/sync-backup/restic/internal/fuse/snapshots_dirstruct_test.go

Purpose: focused unit tests for the snapshot pseudo-directory generator.

Important APIs/tests: `TestPathsFromSn` validates `%i`, `%I`, `%T`, `%t`, `%u`, and `%h` expansion and time suffix behavior. `TestMakeDirs` builds multiple snapshots with shared hosts, tags, and timestamps, then asserts the complete entry map and `latest` symlink targets. `verifyEntries` compares snapshot/link maps and checks parent-child pointer integrity. `TestMakeEmptyDirs` verifies static prefixes for empty repositories. `TestFilenameFromTag` covers tag sanitization.

Control flow and state: tests avoid repository I/O by calling `makeDirs` directly on synthetic `data.Snapshot` values with fixed IDs/times. Expected maps include intermediate directories, snapshot mount points, and latest links.

Dependencies and integration points: uses `data.TestSetSnapshotID`, `restic.ParseID`, and restic test assertions. These tests are the primary specification for `SnapshotsDirStructure` output.

Risks and test signals: the complete expected maps make intentional layout changes expensive but catch subtle regressions in naming, suffix generation, and tree linking. Host and username sanitization are not tested because production code does not sanitize them.
