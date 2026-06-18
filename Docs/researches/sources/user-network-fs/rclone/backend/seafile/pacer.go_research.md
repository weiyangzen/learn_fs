# sources/user-network-fs/rclone/backend/seafile/pacer.go

## Purpose
This file provides shared request pacing for Seafile remotes. It ensures that all remotes pointing at the same Seafile host and port reuse one `fs.Pacer`, reducing request bursts against the same server.

## Important APIs, Types, And Functions
Constants configure pacing: minimum sleep 100 ms, maximum sleep 10 s, and decay constant 2. Package globals `pacers` and `pacerMutex` store shared pacers by normalized remote key. `init` initializes the map. `getPacer` parses the remote, returns an existing pacer if present, or creates a new default pacer with the configured bounds. `parseRemote` normalizes a URL to `hostname:port`, defaulting to 443 for HTTPS and 80 otherwise.

## Control Flow
`getPacer` locks the map, normalizes the remote URL, checks for an existing pacer, creates one if absent, stores it, and returns it. `parseRemote` uses `url.Parse`; on parse failure it logs and returns the shared key `default`.

## State And Persistence Behavior
State is process-local and global to the package. Pacers persist for the lifetime of the process and are never removed from the map. This is intentional for remote reuse but means many distinct hosts could accumulate pacers over a long-running process.

## Dependencies And Integration Points
The file depends on rclone `fs` and `lib/pacer`, standard URL parsing, sync, and time. Other Seafile backend code calls `getPacer` during backend construction or API setup.

## Risks And Edge Cases
The map key ignores URL scheme except for default-port selection, so `http://host:443` and `https://host` can share `host:443` despite differing schemes. Paths are ignored, which is correct for server-level pacing. Invalid remotes all share `default`, which prevents crashes but can couple unrelated malformed configurations. No cleanup exists for the global map.

## Test Signals
No tests in this subset cover pacer normalization or sharing. Useful tests would cover explicit ports, default HTTPS/HTTP ports, invalid URLs, and same-host remote reuse.
