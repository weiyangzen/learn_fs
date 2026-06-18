# sources/sync-backup/syncthing/lib/ur/memsize_windows.go

Purpose: Windows implementation of physical memory size for usage reports.

Important APIs and control flow: defines lazy proc lookup for `kernel32.dll` `GetPhysicallyInstalledSystemMemory`. `memorySize` calls the proc with a pointer to a kilobyte output value, checks `res == 0` for failure, and returns kilobytes converted to bytes.

State and persistence: no state beyond lazy DLL/proc handles.

Dependencies and integration: uses `golang.org/x/sys/windows`; called by usage-report generation.

Risks: API returns installed physical memory, which may differ from available/container memory. Failure returns zero. No tests in this subset.
