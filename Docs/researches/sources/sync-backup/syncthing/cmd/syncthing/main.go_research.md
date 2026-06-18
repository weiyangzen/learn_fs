# sources/sync-backup/syncthing/cmd/syncthing/main.go

Purpose: primary Syncthing command entrypoint, command tree, serving lifecycle, upgrade logic, debug commands, and startup/shutdown orchestration.

Important APIs/types/functions: top-level `CLI`, `serveCmd`, `defaultVars`, `main`, `helpHandler`, `serveCmd.Run`, `openGUI`, `checkUpgrade`, `upgradeViaRest`, `syncthingMain`, `setupSignalHandling`, `loadOrDefaultConfig`, `auditWriter`, `autoUpgrade`, `initialAutoUpgradeCheck`, `cleanConfigDirectory`, `setPauseState`, command structs for version/device-id/paths/upgrade/browser/debug, database debug commands, `setConfigDataLocationsFromFlags`, and `migratingAPI`.

Control flow: `main` builds a Kong parser, handles shell completion and version flag, then runs the selected command. `serveCmd.Run` applies GUI override env vars, console hiding, logging format/level, log and GUI asset locations, ensures config/data directories, and either runs the monitored child or inner Syncthing process. `syncthingMain` starts debug profilers, loads/generates certs, locks the instance, starts early services and config, performs database migration/open, optionally performs initial auto-upgrade, adjusts pause state, creates the Syncthing app with audit/profiler options, starts auto-upgrade and signal handlers, starts the app, cleans old config/data artifacts, optionally opens browser, waits for app exit, stops CPU profiling, unlocks, and exits with service status.

State and persistence: manages config/data locations, cert/key files, lock file, database, audit logs, cleanup of old panic/audit/config/support files, upgrade metadata in misc DB, and optional profile files. Direct debug commands can remove the database or inspect SQLite statistics/files.

Dependencies/integration: central integration point for `cli`, `decrypt`, `generate`, database/sqlite, config/events/locations, `lib/syncthing`, upgrade, Suture services, flock, OS signals, logging, and monitor mode.

Risks and test signals: startup has many exit paths with process termination rather than returned errors. Upgrade timing gates prevent repeated early upgrade attempts. `loadOrDefaultConfig` creates a temporary wrapper on any load error, not only missing files, which is acceptable for some commands but risky if callers expect strict config validation. `setConfigDataLocationsFromFlags` enforces `--config` and `--data` together. No tests in this subset directly cover main lifecycle.
