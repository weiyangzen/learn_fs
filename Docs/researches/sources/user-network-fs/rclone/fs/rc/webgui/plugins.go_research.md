# sources/user-network-fs/rclone/fs/rc/webgui/plugins.go

## Purpose
This file implements WebGUI plugin metadata storage, plugin filtering, GitHub URL parsing, and plugin serving/proxy helpers.

## Important APIs, Types, and Functions
- `PackageJSON` and `RcloneConfig` model plugin `package.json` metadata and rclone-specific fields.
- `Plugins` stores loaded plugin metadata plus a mutex and config filename.
- `initPluginsOrError` initializes cache paths and loads `availablePlugins.json` when WebUI is enabled.
- `readFromFile`, `writeToFile`, `addPlugin`, `removePlugin`, and `GetPluginByName` persist and query plugin state.
- `getAuthorRepoBranchGitHub` parses supported GitHub repository URLs.
- `filterPlugins` selects plugin subsets.
- `ServePluginOK` reverse-proxies test plugins.
- `ServePluginWithReferrerOK` redirects absolute asset requests back under a plugin path when configured.

## Control Flow
Initialization is guarded by `initMutex` and `initSuccess`. Plugin metadata is read from or created under `PluginsPath/config/availablePlugins.json`. Test-plugin serving matches `/plugins/{author}/{name}/...`, looks up plugin metadata, and proxies to `TestURL` when `Rclone.Test` is true. Referrer-based serving inspects `Referer`, finds the plugin that emitted the request, and redirects when `RedirectReferrer` is set.

## State and Persistence
Plugin metadata persists as JSON under the WebGUI cache plugin config directory. Package globals hold paths, the loaded plugin set, a reverse proxy, regexes, and init flags. Writes use file mode `0755` even for JSON metadata.

## Dependencies and Integration Points
It depends on `config.GetCacheDir`, `fs` logging, `rc.Opt.WebUI`, and `net/http/httputil`. `rcserver.handleGet` uses `PluginsMatch`, `PluginsPath`, `ServePluginOK`, and `ServePluginWithReferrerOK`.

## Risks and Edge Cases
The global `pluginsProxy.Director` is mutated per request, which could race under concurrent test-plugin proxy requests. GitHub URL parsing is narrow and defaults to `master`. Persisted plugin config is process-global and can be affected by tests or multiple RC servers. Referrer parsing assumes a host:port-style URL and may miss valid referrers.

## Test Signals
`webgui/rc_test.go` indirectly exercises plugin metadata loading, add/list/remove/filter RC paths, but it relies on live network downloads for `TestAddPlugin` unless skipped on bad HTTP status.
