## sources/sync-backup/syncthing/lib/osutil/lowprio_unix.go

Purpose: generic Unix priority lowering for non-Windows, non-Linux, non-iOS targets and Android.

Important API: `SetLowPriority` checks current process priority and calls `syscall.Setpriority` to set nice level 9 when needed.

Control flow and state: if current nice is already at or below desired priority, returns nil; otherwise attempts to set priority for process zero.

Dependencies and integration points: platform API counterpart to Linux and Windows implementations.

Risks: build expression includes Android via the `|| android` part; priority syscalls can fail due to platform permissions.

Test signals: no direct tests.
