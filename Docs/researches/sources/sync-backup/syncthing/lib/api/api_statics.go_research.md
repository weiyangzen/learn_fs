# sources/sync-backup/syncthing/lib/api/api_statics.go

Purpose: Static GUI asset server with theme support and development override directory support.

Important APIs/types/functions: `staticsServer` stores asset override directory, compiled asset map, available themes, current theme, and last theme-change time. `newStaticsServer`, `ServeHTTP`, `serveAsset`, `serveFromAssetDir`, `serveFromAssets`, `serveThemes`, `setTheme`, and `String` implement serving and theme changes.

Control flow: Requests to `/themes.json` return theme names. Other paths normalize `/` to `index.html`, resolve the current theme, honor `theme-assets/<theme>/<file>` explicit theme paths, then try override current theme, compiled current theme, override default theme, compiled default theme, and finally 404. `setTheme` updates theme and modification timestamp under lock.

State and persistence behavior: Current theme and last-change time are in-memory. Override files are read from disk through `http.ServeFile`; compiled assets are served from memory.

Dependencies and integration points: Uses `lib/api/auto.Assets`, `lib/assets.Serve`, and config default theme. `api.go` mounts this at `/`, and `CommitConfiguration` updates the theme.

Risks: Asset override directory can shadow compiled GUI assets and must be trusted. Cache is disabled at the static server level, while asset ETags still exist lower down. Available themes are collected once at server creation and do not update if directories appear later.

Test signals: `TestAssetsDir` verifies override precedence. `TestDirNames` verifies sorted directory listing used for theme discovery.
