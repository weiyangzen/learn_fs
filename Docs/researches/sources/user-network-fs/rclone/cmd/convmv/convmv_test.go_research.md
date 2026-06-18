<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv_test.go -->
# sources/user-network-fs/rclone/cmd/convmv/convmv_test.go

## Purpose

`convmv_test.go` validates transform behavior across representative name transformations and Unicode normalization cases.

## Important APIs, Types, and Functions

`TestMain` initializes fstest. `TestTransform` runs a table of transform/back-transform pairs, creates local and remote files with varied names, applies `sync.Transform`, compares names with `compareNames`, and checks lossless round trips where expected. Helpers include `makeTestFiles`, `deleteDSStore`, `compareNames`, `transformItems`, and `detectEncoding`. `TestUnicodeEquivalence` verifies NFC conversion for a decomposed name.

## Control Flow

Each test creates an fstest run, prepares local/remote fixtures, sets transform options, runs transforms, lists remote entries, and compares transformed expectations.

## State and Persistence Behavior

Tests create and mutate temporary local and remote files and clean `.DS_Store` artifacts that may appear on macOS.

## Dependencies and Integration Points

It integrates fstest, all backends, filter rules, operations delete, walk listing, sync transform, `lib/transform`, and Unicode normalization.

## Risks and Test Signals

Signals include broad transform coverage and Unicode equivalence. Gaps include direct command flag plumbing, collision/race behavior, dry-run, and large trees. Tests also rely on a reduced ASCII alphabet, so non-ASCII path coverage is narrower than the commented fixture suggests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv_test.go -->
