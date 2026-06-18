# sources/sync-backup/syncthing/cmd/dev/stfinddevice/main.go

Purpose: development utility for querying global discovery servers for a device ID and printing advertised addresses.

Important APIs/types/functions: flags `-server` and `-timeout`; `checkResult`, `checkServers`, `checkServer`, and `usage`. It uses `protocol.DeviceIDFromString`, `config.DefaultDiscoveryServers`, `discover.NewGlobal`, and `Lookup`.

Control flow: parses exactly one device ID, chooses either one supplied server or the default discovery server list, launches one goroutine per server, and prints each result with elapsed time, errors, and addresses. Each `checkServer` races lookup against a `time.AfterFunc` timeout.

State and persistence behavior: no persistence. Runtime state is per-server goroutine result channels and timeout timers.

Dependencies/integration: depends on Syncthing discovery libraries, TLS configuration, global discovery server URLs, and network reachability.

Risks/test signals: timeout goroutine can race with lookup result and write to buffered channel; the first result wins. Signal is printed addresses or timeout/error messages per discovery server.
