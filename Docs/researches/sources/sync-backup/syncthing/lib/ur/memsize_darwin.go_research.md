# sources/sync-backup/syncthing/lib/ur/memsize_darwin.go

Purpose: Darwin implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` runs `syscall.SysctlUint64("hw.memsize")` and returns the value as `int64`, or zero on error.

State and persistence: no state.

Dependencies and integration: called by `ur.Service.reportData` to populate `MemorySize` in MiB.

Risks: errors collapse to zero, so reports can omit meaningful memory size silently. Platform-specific and untested in this subset.
