# sources/sync-backup/syncthing/cmd/dev/stevents/main.go

Purpose: command-line utility that tails Syncthing REST events and prints them as indented JSON.

Important APIs/types/functions: `event` struct models REST event fields `id`, `type`, `time`, and `data`. Flags are `-target`, `-types`, and required `-apikey`.

Control flow: after validating API key, it loops forever issuing `GET http://<target>/rest/events?since=<id>[&events=...]` with `X-API-Key`, decodes the JSON event array, prints each event, and advances `since` to the last event ID.

State and persistence behavior: no persistence. Runtime cursor is the `since` integer, held only in memory.

Dependencies/integration: depends on a running Syncthing GUI/API endpoint and the events REST API. It uses Go's default HTTP client without custom timeout.

Risks/test signals: missing timeout can hang; fatal errors exit on transient HTTP or JSON failures. Signal is continuous JSON event output and monotonically increasing event IDs.
