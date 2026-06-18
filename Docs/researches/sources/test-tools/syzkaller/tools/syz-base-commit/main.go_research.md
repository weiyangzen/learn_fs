<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-base-commit/main.go -->
# sources/test-tools/syzkaller/tools/syz-base-commit/main.go

## Purpose

Debug tool for blob-based base commit detection.

## Important APIs, Types, and Functions

Flag `--sourcedir`; reads diff; `vcs.Git.BaseForDiff` with `debugtracer.GenericTracer`.

## Control Flow

Validates repo and diff args, reads diff, runs base detection, logs no candidates or candidate commits/branches.

## State and Persistence Behavior

Reads repo/diff; writes logs only.

## Dependencies and Integration Points

Depends on full Git repo and `pkg/vcs`; commit graph recommended for speed.

## Risks and Edge Cases

Diagnostic text output is not stable API; large repos are slow without commit graph.

## Test Signals

Known patch fixtures with expected base candidate hashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-base-commit/main.go -->
