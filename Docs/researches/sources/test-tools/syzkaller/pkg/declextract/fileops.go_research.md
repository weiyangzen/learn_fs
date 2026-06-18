# sources/test-tools/syzkaller/pkg/declextract/fileops.go

Purpose: `fileops.go` synthesizes syzkaller descriptions and interface records for Linux `file_operations` tables, mapping callback coverage from ifaceprobe to concrete file paths and ioctl commands.

Important APIs/functions: `serializeFileOps` seeds known ioctl argument types, resolves callbacks, maps file operations to probed files, records `FILEOP` and `IOCTL` interfaces, and emits generated open/read/write/mmap/ioctl descriptions. `createFops` emits resources and operations for one file operation table. `createIoctls` emits command-specific or generic ioctl calls. Mapping helpers include `mapFopsToFiles`, `mapFileToFops`, `fileCandidates`, and `resolveFopsCallbacks`.

Control flow and state: callback names are resolved to `Function` pointers and counted for uniqueness. Probe coverage is converted into file-to-callback sets, then scored against candidate file operation tables. Unique callbacks dominate scoring; ioctl matches receive a high bonus; excessive duplicate read/write/mmap-only descriptions are filtered. A generic open-only entry is appended for files with no stronger mapping.

Dependencies and integration: this module uses `ifaceprobe.Info` from `context.probe`, `ast.IsValidStringLit` to reject non-ASCII/invalid filenames, `clangtool.SortAndDedupSlice` for deterministic candidates, type inference from `typing.go`, and field lowering from `declextract.go`.

Risks: mapping file paths to operation tables is acknowledged as heuristic-heavy because callbacks can be shared, chained, updated at runtime, or not covered by probe runs. `mustFindFunc` panics for missing callback functions. Generated descriptions can be generic when coverage cannot prove a precise file operation. No direct tests are present in this subset.
