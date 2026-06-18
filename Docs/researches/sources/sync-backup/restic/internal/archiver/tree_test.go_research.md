# sources/sync-backup/restic/internal/archiver/tree_test.go

Purpose: Tests virtual target-tree construction and path normalization.

Important APIs and functions: `testBackupTargets` marks paths explicit. `TestPathComponents`, `TestRootDirectory`, and `TestTree` cover `pathComponents`, `rootDirectory`, `newTree`, `Add`, and `unrollTree`.

Control flow and state: Tests build expected `tree` values for simple files, multiple roots, relative parent paths, duplicate/colliding basenames, nested targets, unrolled parent/child target combinations, Windows volumes/UNC roots, and invalid `.`/`..` direct tree inputs. Temporary source trees are created when unroll behavior requires real directory contents.

Dependencies and integration: Uses `fs.NewLocal`, `TestCreateFiles`, `internal/test`, `go-cmp`, OS path normalization, and runtime OS skips.

Risks and test signals: This file is the key signal for stable snapshot path layout. It catches regressions in collision suffixing, duplicate target removal, explicit flags, virtual Windows prefixes, relative root detection, and unroll collision errors.
