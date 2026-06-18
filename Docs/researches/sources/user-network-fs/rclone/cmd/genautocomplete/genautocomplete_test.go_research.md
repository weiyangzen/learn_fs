<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go

## Purpose

`genautocomplete_test.go` verifies completion script generation for bash, zsh, and fish file and stdout paths.

## Important APIs, Types, and Functions

Tests create temporary files, invoke shell command `Run` functions directly, read output, and assert it is non-empty. Stdout tests temporarily replace `os.Stdout` with a temp file.

## Control Flow

Each test creates a temp file, defers close/remove, runs the command with either the temp path or `-`, then reads and asserts content.

## State and Persistence Behavior

Only temporary local files are created. Global `os.Stdout` is mutated briefly and restored with defer.

## Dependencies and Integration Points

It uses `testify/assert`, OS temp files, and the package command definitions.

## Risks and Test Signals

Signals are basic generation health. Gaps include PowerShell coverage, default privileged paths, content correctness, concurrency safety around `os.Stdout`, and command tree completeness assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go -->
