## sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest.go

This file manages the lore manifest used to discover archive epoch git repositories. `InboxInfo` exposes `EpochURL` and `LastEpochURL`; `ParseManifest` converts `manifest.js` keys into inbox epoch counts; `QueryManifest` downloads and gunzips `manifest.js.gz`; `ManifestSource` continuously refreshes and serves the latest successful manifest.

`ParseManifest` scans JSON object keys with `/([\w-]+)/git/(\d+)\.git`, logs unexpected keys, and stores the maximum epoch plus one per inbox. `ManifestSource.Loop` retries every 15 minutes until the first successful load, closes `firstLoaded`, then refreshes every 12 hours. `Get` blocks until the first load or context cancellation and returns the latest map under a mutex.

State is in memory, refreshed from network. Integration is with `SeriesFetcher.Update`. Risks include using `http.Get` without caller context, no HTTP status validation before gzip, returning the internal map without deep copy, and callers blocking indefinitely if context never cancels and manifest never loads. Unit tests cover parsing and epoch URL construction.
