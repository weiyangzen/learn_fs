## sources/sync-backup/syncthing/lib/osutil/rlimit_unix.go

Purpose: Unix implementation for maximizing the open-file resource limit.

Important API: `MaximizeOpenFileLimit` reads `RLIMIT_NOFILE`, raises current soft limit toward hard limit or a package cap, writes it back with `Setrlimit`, and returns the resulting current limit.

Control flow and state: if get/set rlimit fails, it returns the current known limit and wrapped error. Constants bound the target to avoid overflow or unreasonable values.

Dependencies and integration points: used during startup to allow many folder/file descriptors.

Risks: permissions, systemd limits, containers, or macOS limits can prevent raising the soft limit. Callers must treat errors as non-fatal where appropriate.

Test signals: no direct tests in this subset.
