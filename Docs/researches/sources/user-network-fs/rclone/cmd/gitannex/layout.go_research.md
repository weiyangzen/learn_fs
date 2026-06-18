<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/layout.go -->
# sources/user-network-fs/rclone/cmd/gitannex/layout.go

## Purpose

`layout.go` maps git-annex key layout modes to rclone filesystem strings so the built-in remote can match `git-annex-remote-rclone` storage layouts.

## Important APIs, Types, and Functions

`layoutMode` constants cover `lower`, `directory`, `nodir`, `mixed`, `frankencase`, and unknown. `allLayoutModes` returns supported modes. `parseLayoutMode` validates strings. `queryDirhashFunc` abstracts protocol dirhash queries. `buildFsString` joins remote name and prefix, optionally queries `DIRHASH-LOWER` or `DIRHASH`, and appends path components according to mode.

## Control Flow

`nodir` returns the prefix path directly. Lower/directory modes request lowercase dirhash; mixed/frankencase request normal dirhash. Directory mode appends key to the dirhash path, while frankencase lowercases the returned dirhash.

## State and Persistence Behavior

The file is stateless. Its output determines where persistent key objects are stored.

## Dependencies and Integration Points

It integrates with git-annex dirhash protocol messages, `fspath.JoinRootPath`, and transfer/check/remove handlers.

## Risks and Test Signals

Risks include path compatibility regressions, bad trailing colon handling, untested unknown-mode panic paths, and differences from external helper layouts. Tests should cover all modes, dirhash query failures, remote names with/without colon, prefixes, realistic keys, and cross-compatibility e2e tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/layout.go -->
