# sources/user-network-fs/rclone/cmd/gui/gui_test.go

Purpose: exercises the GUI HTTP-serving helpers, especially login URL construction, origin normalization, GUI asset source selection, and SPA/static asset serving. The tests are in package `gui`, so they cover unexported helpers such as `buildLoginURL`, `originFromURL`, `guiSourceFS`, and `guiHandler`.

Important functions: `writeTestDir` and `writeTestZip` create temporary GUI bundles; `handlerForSource` wraps directory/zip sources in the production handler; `newTestHandler` uses embedded assets and skips when the dist bundle is unavailable. Test cases verify directory and zip `fs.FS` handling, missing/invalid source errors, index serving, asset serving, fallback routing, and gzip content negotiation.

Control flow and state: tests allocate temporary files with `t.TempDir`, register cleanup callbacks for source filesystems, then use `httptest` with a chi router/middleware-like handler stack. Persistence is limited to temporary test fixtures and skipped embedded-bundle tests.

Dependencies/integration: standard `archive/zip`, `compress/gzip`, `io/fs`, `httptest`, chi, and testify. Risks are mostly fixture drift with the real GUI bundle and content-encoding behavior. Test signal is strong for handler behavior but intentionally conditional for embedded assets.
