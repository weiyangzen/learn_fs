<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap.go -->
# sources/security-integrity/gocryptfs/internal/inomap/inomap.go

- Purpose: Maps backing filesystem device/inode pairs to stable FUSE inode numbers, spilling uncommon devices into a separate namespace when needed.
- Important APIs/types/functions: `type InoMap struct`, `const (`, `var spillWarn sync.Once`, `func New(rootDev uint64) *InoMap`, `func (m *InoMap) NextSpillIno() (out uint64)`, `func (m *InoMap) spill(in QIno) (out uint64)`, `func (m *InoMap) Translate(in QIno) (out uint64)`, `func (m *InoMap) TranslateStat(st *syscall.Stat_t)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; treats invalid internal invariants as fatal/panic conditions. Source size is 3645 bytes across 132 lines, read as part of this work item.
- Dependencies and integration points: standard library: log, math, sync, sync/atomic, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/inomap.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap.go -->
