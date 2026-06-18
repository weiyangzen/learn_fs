<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree_test.go -->
# sources/user-network-fs/rclone/cmd/tree/tree_test.go

## Purpose

`tree_test.go` gives a focused golden-output test for `Tree` rendering over the repository's `testfiles` fixture.

## Important APIs, Types, and Functions

The sole `TestTree` initializes fstest, opens a local fs for `testfiles`, calls `Tree` with a fresh `tree.Options`, and compares the exact text output.

## Control Flow

The test bypasses Cobra and global flags, writes output into a `bytes.Buffer`, and expects the root, three files, one subdirectory, two nested files, and footer counts.

## State and Persistence Behavior

It performs read-only fixture access and has no persistent state. It depends on the local backend being registered by blank import.

## Dependencies and Integration Points

The test verifies integration among `fs.NewFs`, `walk.NewDirTree`, the tree adapter, and external renderer formatting.

## Risks and Test Signals

The golden string is sensitive to renderer glyphs and ordering. It does not cover command flags, output files, color, filters, path encoding, or sort modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree_test.go -->
