# sources/sync-backup/syncthing/lib/syncthing/debug.go

Purpose: package-level logging setup and debug-level check for the main run facility.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("Main run facility")`. `shouldDebug` asks the default slog logger whether debug is enabled for a background context; `App.stopWithErr` uses it before printing the service tree.

State and persistence: logger adapter only.

Dependencies and integration: integrates with Syncthing logging and app shutdown diagnostics.

Risks and signals: no tests needed for simple logger wiring. Behavior depends on current global logger configuration.
