# sources/sync-backup/syncthing/cmd/infra/stupgrades/main.go

Purpose: implements the upgrade metadata proxy service used by Syncthing clients. It periodically fetches GitHub release metadata, enriches releases with compatibility data, filters responses by client OS version, serves latest stable/prerelease metadata, and can forward configured auxiliary paths through a caching proxy.

Important APIs/types/functions: `cli`, `server`, `githubReleases`, `servePing`, `serveReleases`, `proxy.ServeHTTP`, `filterForLatest`, `filterForCompatibility`, `cachedReleases`, `cachedReleases.Update`, `fetchGithubReleases`, and `addReleaseCompatibility`.

Control flow: `main` parses Kong flags and calls `server`. `server` starts an optional metrics listener, performs an initial cache update, starts periodic refreshes, registers `/ping` and `/meta.json`, then attaches any `path->url` forwards with `httpcache.SinglePath`. `serveReleases` reads cached releases, optionally filters them based on `User-Agent` and `Syncthing-Os-Version`, keeps only the latest relevant releases, sets cache/CORS/Vary headers, and returns JSON.

State and persistence: release cache is in memory under `cachedReleases.mut`. `latestRel` and `latestPre` are mirrored into a gauge. There is no durable local storage; refresh failures retain the last successful cache.

Dependencies/integration: uses GitHub releases JSON shaped as `upgrade.Release`, Syncthing upgrade compatibility semantics, Prometheus, `httpcache`, Kong, and optional HTTP forwarding targets.

Risks and test signals: `fetchGithubReleases` accepts a context parameter but creates the initial request with `context.TODO()`, so cancellation does not cover the releases fetch. HTTP status codes from GitHub are not checked before JSON decode. Compatibility files are limited to 10 KiB. Metrics identify filter outcomes. No tests are listed in this subset for filtering or proxy behavior.
