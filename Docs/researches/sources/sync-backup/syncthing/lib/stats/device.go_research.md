# sources/sync-backup/syncthing/lib/stats/device.go

Purpose: stores and retrieves per-device runtime statistics backed by Syncthing's typed key-value database.

Important APIs and control flow: `DeviceStatistics` is the JSON-facing shape with `LastSeen` and `LastConnectionDurationS`. `DeviceStatisticsReference` wraps `*db.Typed`. `GetLastSeen` reads the `lastSeen` key and defaults missing data to Unix epoch rather than zero time. `GetLastConnectionDuration` reads `lastConnDuration` as nanoseconds and defaults missing data to zero. `WasSeen` writes current time truncated to seconds. `LastConnectionDuration` stores `time.Duration.Nanoseconds`. `GetStatistics` composes both fields.

State and persistence: persists typed keys `lastSeen` and `lastConnDuration` in the supplied database namespace.

Dependencies and integration: used by model/device statistics surfaces and API JSON output. Depends on `internal/db`.

Risks: database errors propagate, but partial updates are possible because operations are separate. Time truncation intentionally drops subsecond precision. Test coverage confirms basic write/read behavior.
