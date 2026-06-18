# sources/sync-backup/syncthing/lib/syncthing/superuser_windows.go

Purpose: Windows implementation of privileged/system-user detection.

Important APIs and control flow: `isSuperUser` opens the current process token, gets the token user, converts its SID to string, and compares it with the LocalSystem RID `S-1-5-18`. Errors are logged at debug and return false.

State and persistence: no state.

Dependencies and integration: called by app startup warning path. Depends on `syscall` token APIs and logging.

Risks: detects LocalSystem specifically, not all administrator contexts. Fail-open-to-false avoids startup failures but can suppress warnings when token APIs fail. No tests in this subset.
