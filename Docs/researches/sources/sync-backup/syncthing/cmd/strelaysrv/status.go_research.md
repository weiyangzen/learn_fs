# sources/sync-backup/syncthing/cmd/strelaysrv/status.go

Purpose: exposes the relay server status HTTP endpoint and calculates throughput rates.

Important APIs/types/functions: global `rc`, `statusService`, `getStatus`, `rateCalculator`, `newRateCalculator`, `updateRates`, and `rate`.

Control flow: `statusService` creates a 360-interval rate calculator at 10-second resolution, registers `/status`, optionally exposes pprof, and serves HTTP with keepalives disabled. `getStatus` gathers build/runtime data, pending and active session counts under lock, connection/proxy/byte atomics, rate windows, and current relay options, then emits indented JSON with CORS.

State and persistence: rate history is an in-memory ring-like slice shifted every interval. Status is computed live from globals and atomics.

Dependencies/integration: consumed by relay pool stats scraping, depends on build metadata, runtime package, session globals, and option globals.

Risks and test signals: `rate(periods)` assumes enough history length for the requested period. Locking around sessions prevents map/slice races for counts. No direct tests cover status JSON or rate calculation.
