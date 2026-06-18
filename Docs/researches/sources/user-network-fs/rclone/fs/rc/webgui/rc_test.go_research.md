# sources/user-network-fs/rclone/fs/rc/webgui/rc_test.go

## Purpose
This file tests the WebGUI plugin RC endpoints and plugin metadata operations.

## Important APIs, Types, and Functions
- `setCacheDir` points plugin paths at a temporary directory and initializes `loadedPlugins`.
- `addPlugin` invokes `pluginsctl/addPlugin` with a test GitHub URL and skips on selected bad HTTP status failures.
- `removePlugin` verifies removal of a missing plugin produces an error.
- Tests cover add, list, remove, and filtering by type/plugin type.

## Control Flow
An `init` function sets `rc.Opt.WebUI = true` so plugin initialization succeeds. Tests fetch handlers from `rc.Calls`, call them directly with `context.Background`, and inspect `loadedPlugins` or returned `rc.Params`.

## State and Persistence
Tests write plugin config and downloaded/unzipped plugin content under temporary cache directories. The global `rc.Opt.WebUI`, `PluginsPath`, `pluginsConfigPath`, and `loadedPlugins` are mutated.

## Dependencies and Integration Points
The tests exercise the global RC registry, WebGUI plugin helpers, filesystem cache paths, and live GitHub release/package downloads for adding the test plugin.

## Risks and Edge Cases
Network-dependent tests can be flaky and only skip a subset of download failures. Global state mutation can leak if tests are reordered or run with other WebGUI tests. Commented-out tests indicate test-plugin removal/listing coverage is currently disabled.

## Test Signals
The file confirms handlers are registered and basic plugin lifecycle paths work in the happy path. It has weaker coverage for proxy/referrer serving, failed unzip/download cleanup, and file removal on plugin deletion.
