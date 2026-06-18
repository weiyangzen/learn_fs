<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cat/cat.go -->
# sources/user-network-fs/rclone/cmd/cat/cat.go

## Purpose

`cat.go` implements `rclone cat`, streaming one file or a filtered tree of files to stdout, discard, or another writer, with optional byte-range selection and separators between objects.

## Important APIs, Types, and Functions

Package globals hold flag state: `head`, `tail`, `offset`, `count`, `discard`, and `separator`. `init` registers the command and flags. The Cobra `Run` validates mutually exclusive range modes, normalizes `--head` and `--tail` into `offset`/`count`, builds the source Fs with `cmd.NewFsSrc`, chooses `os.Stdout` or `io.Discard`, and calls `operations.Cat`.

## Control Flow

Argument validation happens before Fs construction. Transfer execution is delegated to `cmd.Run(false, false, ...)`, so no retry loop or stats display is requested by this command.

## State and Persistence Behavior

Remote state is read-only. Local output is stdout unless `--discard` is set; no persistent files are created by this wrapper.

## Dependencies and Integration Points

It depends on Cobra, rclone flag helpers, `cmd` Fs helpers, filtering inherited from the root command, and `fs/operations.Cat`.

## Risks and Test Signals

Risks include conflicting range flags, negative offsets on unknown-size objects, separator escaping expectations, and stdout binary output. Tests should cover range normalization, conflict rejection, discard behavior, multi-file separators, single-file filters, and operation errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cat/cat.go -->
