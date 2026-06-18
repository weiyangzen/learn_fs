# sources/sync-backup/restic/internal/archiver/exclude_test.go

Purpose: Unit tests for archiver exclusion predicates.

Important APIs and functions: `TestIsExcludedByFile` covers `isExcludedByFile`; `TestMultipleIsExcludedByFile` validates multiple `RejectIfPresent` instances together; `TestIsExcludedByFileSize` validates `RejectBySize`; `TestDeviceMap` validates `deviceMap.IsAllowed`.

Control flow and state: Tests create temporary directory trees and tag files, then run predicate logic either directly or through `filepath.Walk`. Inclusion decisions are collected in maps and compared against expected values.

Dependencies and integration: Uses `internal/fs.NewLocal`, `fs.ExtendedStat`, `internal/test`, OS file creation, truncation, and path normalization. The tests are close to backup traversal behavior but do not run the full archiver.

Risks and test signals: These tests protect against tag-file specs canceling each other out, incorrect tag signature interpretation, directories being rejected by size, and accidental crossing of device boundaries. Device tests use synthetic IDs, so they cover logic but not OS stat behavior.
