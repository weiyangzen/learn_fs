# Research: sources/object-store/minio-mc/cmd/pipe_unsupported.go

## sources/object-store/minio-mc/cmd/pipe_unsupported.go

Purpose: non-Linux fallback for pipe buffer tuning.

Important APIs and functions: build tag `//go:build !linux` selects a no-op `increasePipeBufferSize(_ *os.File, _ int) error`.

Control flow: any caller request returns nil immediately, so `mc pipe` proceeds without pipe-size changes on unsupported platforms.

State and persistence: no state changes.

Dependencies and integration: satisfies the same function signature used by `pipe-main.go`, preserving cross-platform compilation.

Risks and tests: hidden `--pipe-max-size` has no effect on non-Linux systems, and callers receive no warning. No tests cover this fallback.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_unsupported.go -->
