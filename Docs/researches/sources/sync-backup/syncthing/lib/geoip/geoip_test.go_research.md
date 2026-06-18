# sources/sync-backup/syncthing/lib/geoip/geoip_test.go

## Purpose
Integration test for downloading and opening a MaxMind GeoLite2 City database.

## Important APIs, Types, and Functions
`TestDownloadAndOpen` reads `GEOIP_ACCOUNT_ID` and `GEOIP_LICENSE_KEY`, constructs a provider, and calls `City` for `8.8.8.8`.

## Control Flow
The test skips when credentials are missing, otherwise downloads into `t.TempDir`, opens the DB through `NewGeoLite2CityProvider`, and verifies a lookup does not error.

## State and Persistence Behavior
Downloads database files into a temporary directory and opens a reader.

## Dependencies and Integration Points
Requires external MaxMind service access and valid credentials. Covers `geoip.go` constructor, download path, and lookup path.

## Risks
Network and credential dependency make this unsuitable for default deterministic CI unless secrets are configured. It does not exercise refresh cleanup behavior.

## Test Signals
Good live integration signal for initial download and DB readability, but not for scheduled refresh or failure modes.
