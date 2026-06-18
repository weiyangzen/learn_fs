# sources/sync-backup/syncthing/lib/geoip/geoip.go

## Purpose
Provides an automatically updating MaxMind GeoLite2 City database provider with thread-safe IP lookup.

## Important APIs, Types, and Functions
`Provider` stores edition/account/license/refresh settings, database directory, mutex, current DB directory, and `*geoip2.Reader`. Public APIs are `NewGeoLite2CityProvider`, `City`, and `Serve`; internal `download` performs update/open/swap.

## Control Flow
Constructor initializes a provider and performs an initial download. `Serve` waits for context cancellation or refresh interval ticks, downloading on each tick. `download` creates a temp subdirectory, configures `geoipupdate`, downloads the edition, opens the `.mmdb`, swaps it under lock, closes the prior reader, and removes an old directory.

## State and Persistence Behavior
Persists downloaded MaxMind database files under the configured directory. Runtime state tracks the active reader and current DB subdirectory. `City` is mutex-protected.

## Dependencies and Integration Points
Uses `maxmind/geoipupdate`, `oschwald/geoip2-golang`, network access to MaxMind, and context cancellation.

## Risks
`download` appears to remove `p.currentDBDir` after assigning it to the new subdirectory when `prevDBDir != ""`; that likely deletes the newly active DB directory instead of the previous one. Failed downloads leave temp directories behind. `Serve` uses `time.After` in a loop and returns the first refresh error.

## Test Signals
`geoip_test.go` performs an integration download only when credentials are provided.
