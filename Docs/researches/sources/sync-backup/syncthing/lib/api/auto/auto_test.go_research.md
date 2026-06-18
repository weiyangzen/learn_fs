# sources/sync-backup/syncthing/lib/api/auto/auto_test.go

Purpose: Verifies that the compiled GUI asset bundle exposes a gzipped default `index.html` containing HTML.

Important APIs/types/functions: `TestAssets` calls `auto.Assets`, checks `default/index.html`, verifies `Gzipped`, decompresses content, and checks for `<html`.

Control flow: Straight-line asset lookup and gzip read.

State and persistence behavior: No persistence; reads compiled asset map in memory.

Dependencies and integration points: Tests the generated asset package used by `api_statics.go`.

Risks: Under the `noassets` build tag, the fallback asset must still satisfy this test. The test only checks minimal presence, not full GUI asset completeness.

Test signals: Build-time guard that an asset bundle exists and is gzip-compatible.
