<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree.go -->
# sources/user-network-fs/rclone/cmd/tree/tree.go

## Purpose

`tree.go` implements `rclone tree`, adapting rclone directory listings to the `github.com/a8m/tree` renderer to print a Unix-tree-like view of remotes.

## Important APIs, Types, and Functions

The command stores global `tree.Options`, output filename, report toggle, sort selector, and OS path encoder. `Tree(fsrc, outFile, opts)` is the main callable API. `FileInfo` adapts `fs.DirEntry` to `os.FileInfo`, and `Fs` adapts `dirtree.DirTree` to `tree.Fs`.

## Control Flow

The Cobra run path creates the source fs, opens output or terminal output, maps rclone flags into tree options, defaults depth from `--max-depth`, and calls `Tree`. `Tree` walks the remote into a `dirtree.DirTree`, installs the adapter on options, visits and prints the synthetic root, then optionally appends directory/file counts.

## State and Persistence Behavior

The command reads remote listings but does not mutate backends. Output may be persisted when `--output` is used. Package-level options are mutated by Cobra parsing and reused in process.

## Dependencies and Integration Points

It integrates with rclone filtering and fast-list through `walk.NewDirTree`, terminal color handling, OS filename encoding, and the external tree renderer.

## Risks and Test Signals

Risks include global option leakage, path encoding mismatches, missing output-file close handling, directory cache lookup failures, and external renderer behavior changes. Tests should cover sorting flags, depth, output files, encoding, dirs-only, hidden files, and filter interaction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree.go -->
