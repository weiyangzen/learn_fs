# sources/sync-backup/syncthing/lib/ur/memsize_linux.go

Purpose: Linux implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` reads `/proc/meminfo`, parses the first line with `fmt.Sscanf("MemTotal: %d kB\n", &kb)`, and returns kilobytes converted to bytes. Any read/parse error returns zero.

State and persistence: reads procfs only.

Dependencies and integration: feeds `contract.Report.MemorySize`.

Risks: assumes first line format of `/proc/meminfo`; containers may report host memory. Error-to-zero behavior avoids report failures but loses signal. No tests in this subset.
