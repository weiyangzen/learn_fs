# sources/user-network-fs/rclone/backend/chunker/chunker_test.go

## Purpose
This file connects the chunker backend to rclone's generic backend integration test suite.

## Important APIs, Types, And Control Flow
It defines `-bad-chars` to optionally enable invalid-character filename tests when a real remote is configured. `TestIntegration` creates `fstests.Opt` with `NilObject: (*chunker.Object)(nil)`, declares unsupported object and FS methods, and runs `fstests.Run`. Without `-remote`, it synthesizes a `TestChunker:` remote wrapping a local temporary directory and enables quick tests.

## State And Persistence
The generic test suite creates, updates, reads, lists, moves, and removes files through chunker. When no remote is specified, state is under `os.TempDir()/rclone-chunker-test-standard`; otherwise state is on the configured remote.

## Dependencies And Integration Points
It blank-imports `backend/all` so wrapped remotes are available, uses `fstest.RemoteName`, and depends on rclone's backend contract tests. Unsupported method lists document chunker's public feature boundaries.

## Risks And Test Signals
The main signal is that chunker still behaves like an rclone filesystem across standard operations. The bad-character flag documents backend-specific filename constraints. Internal metadata and chunk safety are mostly covered in `chunker_internal_test.go`.
