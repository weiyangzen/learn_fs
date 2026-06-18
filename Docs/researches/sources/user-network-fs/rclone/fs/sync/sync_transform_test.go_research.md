# sources/user-network-fs/rclone/fs/sync/sync_transform_test.go

## Purpose
This file tests integration between sync/move operations and `lib/transform` path transformations. It verifies that transformed file and directory names are applied consistently during sync, move, check, logging, manual transform repair, base64 round trips, and error handling.

## Important APIs, Functions, and Flow
`TestTransform` runs a table of transform configurations including NFC, NFD, base64 encode, prefix/suffix, truncate, encoder/decoder, charmap, lowercase, and ASCII transforms. `makeTestFiles` creates deterministic test names; `deleteDSStore` removes macOS noise; `compareNames` lists remote objects through `walk.ListR`, sorts by transformed name, and checks actual paths against `transform.Path`; `detectEncoding` reports NFC/NFD status. Specific tests cover transformed copy, stacked transforms, file-only, dir-only, all-entry, and no-tag behavior, repeated sync idempotence, syntax validation, canceling transforms, `MoveDir`, `operations.TransformFile`, base64 encode/decode, and illegal path transform errors.

## State, Dependencies, Risks, and Test Signals
Tests set transform options with `transform.SetOptions(ctx, ...)`, create temporary source/destination content with `fstest.Run`, and call `Sync` or `MoveDir`. Some tests switch transform options mid-test to repair remote names. Dependencies include all backends, `fs`, `accounting`, `filter`, `operations`, `walk`, `fstest`, `lib/transform`, Unicode normalization, and sync logger helpers.

Path transforms are risky because they affect directory components, file leaves, empty directories, logger output, check comparisons, and reverse operations. The suite covers lossy transforms, conflicting transforms, illegal transformed names, backend feature fallbacks, repeated runs that must not double-transform, and Unicode normalization. Strong signals come from exact remote listing checks, `compareNames`, logger-vs-lsf checks, and `operations.Check` against transformed names.
