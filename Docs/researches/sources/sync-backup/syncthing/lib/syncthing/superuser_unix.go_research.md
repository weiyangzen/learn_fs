# sources/sync-backup/syncthing/lib/syncthing/superuser_unix.go

Purpose: Unix implementation of privileged-user detection.

Important APIs and control flow: build tags exclude Windows. `isSuperUser` returns `os.Geteuid() == 0`.

State and persistence: no state.

Dependencies and integration: called during app startup to warn when Syncthing runs as root/system. Depends only on `os`.

Risks and signals: simple platform-specific behavior. It treats only effective UID zero as superuser and does not check capabilities or service managers. No tests in this subset.
