# sources/sync-backup/syncthing/lib/ur/memsize_netbsd.go

Purpose: NetBSD implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` calls `unix.SysctlUint64("hw.physmem64")` and returns the result as `int64`, or zero on error.

State and persistence: no state.

Dependencies and integration: uses `golang.org/x/sys/unix`; called by usage-report data generation.

Risks: sysctl failures or unsupported environments silently produce zero. No tests in this subset.
