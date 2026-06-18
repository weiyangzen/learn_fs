# sources/sync-backup/syncthing/lib/syncthing/syncthing.go

Purpose: main embeddable Syncthing app wiring: startup, service supervision, GUI/API setup, shutdown, and lifecycle status.

Important APIs and control flow: `Options` controls audit, upgrades, profiling, delta index reset, and DB maintenance interval. `App` owns config, DB, events, TLS certificate, main Suture supervisor, internals, exit status, error, and shutdown channels. `New` constructs a stopped app. `Start` starts the supervisor background and runs `startup`; failures call `stopWithErr`. `startup` adds failure handling, DB service, optional audit, API event subscriptions, file limit lift, device ID, Starting event, short-ID conflict check, optional profiler and CPU bench, delta reset, dropped-folder DB cleanup, previous-version handling, global migration, model construction, TLS config, discovery/connection service wiring, usage reporting, GUI/API setup, loaded-config logging, superuser warning, StartupComplete event, and optional low-priority setting. `wait` handles supervisor exit, closes DB with timeout, and closes `stopped`.

State and persistence: persists previous build version in misc DB, may drop folder metadata/index IDs, runs global migrations, and config modifications can save via wrappers elsewhere. Shutdown state is guarded by `sync.Once`.

Dependencies and integration: central integration point for db, config, model, connections, discovery, events, API, TLS, upgrade, and usage reporting.

Risks: startup has many side effects; failures after services start must cleanly cancel and close DB. `InsecureSkipVerify` is intentionally used for device-certificate identity verification elsewhere. Tests cover short-ID conflicts and startup failure cleanup.
