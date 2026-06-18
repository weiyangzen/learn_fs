# sources/sync-backup/syncthing/lib/config/debug.go

## sources/sync-backup/syncthing/lib/config/debug.go

Purpose: Provides the package-local logging adapter for configuration loading and saving.

Important APIs/types/functions: Declares package variable `l = slogutil.NewAdapter("Configuration loading and saving")`.

Control flow and state: No control flow; it initializes an adapter at package load time.

Dependencies and integration: Used by config files for debug logging in GUI/STUN handling, migration marker cleanup, wrapper save errors, and Android filesystem detection.

Risks and test signals: Minimal risk. Logging category stability matters for debug filtering; no direct tests.
