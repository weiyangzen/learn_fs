## sources/sync-backup/syncthing/lib/osutil/rlimit_windows.go

Purpose: Windows no-op implementation for open-file limit maximization.

Important API: `MaximizeOpenFileLimit` returns `0, nil`.

Control flow and state: none.

Dependencies and integration points: satisfies cross-platform startup API where Unix rlimits do not apply.

Risks: callers should not interpret zero as a useful limit on Windows.

Test signals: no direct tests.
