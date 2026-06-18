# sources/object-store/minio-mc/cmd/build-constants.go

## Purpose

`build-constants.go` provides build-time metadata variables for version, release tag, commit, short commit, and copyright year.

## Important APIs, Types, and Functions

Package variables are `Version`, `ReleaseTag`, `CommitID`, `ShortCommitID`, and `CopyrightYear`. Defaults are development placeholders, and build tooling can override them with linker flags.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The values are static process state compiled into the binary. No persistence occurs.

## Dependencies and Integration Points

These variables are typically used by version, help, user-agent, and app-info code elsewhere in `mc`.

## Risks and Edge Cases

`ShortCommitID = CommitID[:12]` assumes `CommitID` is at least 12 bytes. The default value satisfies this, but malformed linker injection could panic at initialization.

## Test Signals

Tests should verify defaults are non-empty and build pipelines inject a long enough commit ID.
