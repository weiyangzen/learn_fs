# sources/sync-backup/syncthing/lib/ur/debug.go

Purpose: registers the usage-reporting package for debug logging.

Important APIs and control flow: package `init` calls `slogutil.RegisterPackage("Usage reporting")`.

State and persistence: logger/debug registry side effect only.

Dependencies and integration: connects usage-report logging to Syncthing debug package controls.

Risks and test signals: no logic beyond registration.
