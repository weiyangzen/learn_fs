# sources/sync-backup/syncthing/cmd/strelaysrv/main.go

Purpose: main entrypoint for the Syncthing relay server, including flags, certificates, NAT mapping, relay pool registration, status service, limits, and graceful shutdown.

Important APIs/state/functions: numerous global flag variables, `httpClient`/`httpTransport`, `main`, `monitorLimits`, `mapping`, and `mapping.Address`.

Control flow: `main` parses flags, validates advertised/provided values, binds outgoing HTTP to the listen IP when specific, raises file descriptor limits, loads or generates the relay certificate, configures outbound and inbound TLS, initializes NAT service/mapping, waits briefly for mapping if enabled, creates rate limiters, starts status service, builds the advertised relay URL with query metadata, starts pool join loops unless token mode disables pools, starts the listener, then waits for shutdown signals and closes sessions/outboxes.

State and persistence: certificate/key files persist identity in the keys directory. Live state is global in sessions/outboxes/counters. NAT mappings are runtime. Pool membership is maintained by periodic registration with pools.

Dependencies/integration: uses Syncthing config wrapper, NAT/PMP/UPnP packages, relay protocol, TLS helpers, status and pool files, rate limiting, and OS file descriptor limits.

Risks and test signals: `sessionAddress = addr.IP[:]` assumes resolved advertised IP is non-nil. `InsecureSkipVerify` is set for relay protocol TLS because identity is derived from presented certificates, but this is security-sensitive. Pool joins are disabled when token auth is configured. No direct tests cover startup; behavior is observed through protocol clients/status.
