# sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv.go

Purpose: implements the discovery API server used by Syncthing clients to announce addresses and look up other devices.

Important APIs/types/functions: `announcement`, `apiSrv`, `replicator`, `newAPISrv`, `Serve`, `handler`, `handleGET`, `handlePOST`, `handleAnnounce`, `certificateBytes`, `fixupAddresses`, `loggingResponseWriter`, `addressStrs`, retry header helpers, and `retryAfterTracker`.

Control flow: `Serve` listens with either TLS client-certificate support or plain HTTP for reverse-proxy deployments, registers `/` and `/ping`, and shuts down on context cancellation. `handler` records metrics and dispatches GET/POST. GET parses a `device` query parameter, loads the database record, returns addresses if active, or returns 404 with adaptive `Retry-After` depending on whether the device was ever seen. POST extracts a client certificate from TLS or proxy headers, derives the device ID, decodes announced addresses, normalizes unspecified hosts/ports with the remote address, and merges sorted compacted addresses into the database, optionally sending replication.

State and persistence: live state is in the database implementation. `retryAfterTracker` maintains per-category counters and dynamically adjusts not-found retry delays to target a desired rate. Gzip writers are pooled for compressed lookup responses.

Dependencies/integration: integrates with the `database` interface, AMQP `replicator`, generated discovery protobuf address records, Syncthing device IDs, reverse-proxy certificate header formats for nginx/Caddy/Traefik, and Prometheus metrics.

Risks and test signals: certificate header parsing is security-sensitive in HTTP proxy mode and assumes a trusted proxy boundary. `fixupAddresses` rejects loopback/multicast and enforces scheme/IP-family compatibility, but it calls methods on `ip` after `net.ParseIP(host)` without an explicit nil check; Go IP methods handle nil safely, but this behavior is subtle. Tests cover address fixups, adaptive retry distribution, and API benchmarks, but not certificate header variants or full HTTP TLS flows.
