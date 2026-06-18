# sources/sync-backup/syncthing/lib/upgrade/debug.go

Purpose: package logger adapter for upgrade functionality.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("Upgrade")` for debug logging in release selection and archive processing.

State and persistence: logger only.

Dependencies and integration: integrates upgrade internals with Syncthing logging.

Risks and test signals: no runtime logic beyond logger setup.
