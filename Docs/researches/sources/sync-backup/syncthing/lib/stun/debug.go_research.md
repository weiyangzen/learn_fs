# sources/sync-backup/syncthing/lib/stun/debug.go

Purpose: defines the package logger adapter for STUN functionality.

Important APIs and control flow: initializes package variable `l` with `slogutil.NewAdapter("STUN functionality")`. Other STUN code uses this adapter for debug logging.

State and persistence: package-level logger only; no persistence.

Dependencies and integration: integrates with Syncthing's structured logging utility and package debug controls.

Risks and test signals: no behavior beyond logger registration. Correctness depends on consistent package-level logger naming for diagnostics.
