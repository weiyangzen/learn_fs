<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go -->
# sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go

- Purpose: Tracks open backing files by qualified inode, preserving per-file content locks, file-ID cache, and write operation counters across handles.
- Important APIs/types/functions: `type table struct`, `type Entry struct`, `type countingMutex struct`, `var t table`, `func init()`, `func Register(qi inomap.QIno) *Entry`, `func Unregister(qi inomap.QIno)`, `func (c *countingMutex) Lock()`, `func WriteOpCount() uint64`, `func CountOpenFiles() int`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 2891 bytes across 104 lines, read as part of this work item.
- Dependencies and integration points: standard library: sync, sync/atomic; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/inomap. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go -->
