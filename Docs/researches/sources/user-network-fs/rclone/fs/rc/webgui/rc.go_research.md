# sources/user-network-fs/rclone/fs/rc/webgui/rc.go

## Purpose
This file registers RC endpoints for managing WebGUI plugins.

## Important APIs, Types, and Functions
- Registered paths: `pluginsctl/listTestPlugins`, `pluginsctl/removeTestPlugin`, `pluginsctl/addPlugin`, `pluginsctl/listPlugins`, `pluginsctl/removePlugin`, and `pluginsctl/getPluginsForType`.
- Handler functions include `rcListTestPlugins`, `rcRemoveTestPlugin`, `rcAddPlugin`, `rcGetPlugins`, `rcRemovePlugin`, and `rcGetPluginsForType`.

## Control Flow
Each `init` block registers one call in the global RC registry. Handlers first call `initPluginsOrError`. `rcAddPlugin` parses the repository URL, chooses branch/version defaults, creates plugin directories, downloads `package.json`, resolves the GitHub release asset, downloads and unzips it under `plugins/{author}/{repo}/app`, and records metadata. Listing/filtering handlers reload or filter `loadedPlugins`.

## State and Persistence
The handlers mutate the WebGUI plugin directory tree and `availablePlugins.json`. `rcAddPlugin` removes any previous extract path before unzipping. Output is usually `nil` for mutating operations and maps for listing operations.

## Dependencies and Integration Points
It depends on `rc.Params` typed getters, the plugin helpers in `plugins.go`, and release/download/unzip helpers in `webgui.go`. The endpoints become available to HTTP RC, WASM RC if imported, and CLI `rclone rc`.

## Risks and Edge Cases
Plugin installation performs unauthenticated network downloads from GitHub URLs and extracts archives into the cache, so integrity and zip path safety depend on `GetLatestReleaseURL`, `DownloadFile`, and `Unzip`. Optional `branch` and `version` ignore missing-parameter errors and use defaults. Remove operations fail if the plugin is not loaded but do not remove extracted files from disk.

## Test Signals
`webgui/rc_test.go` verifies registration and behavior for add/list/remove/filter, though add/remove depends on network availability and may skip only selected HTTP failures.
