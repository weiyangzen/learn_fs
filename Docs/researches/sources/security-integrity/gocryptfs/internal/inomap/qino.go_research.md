<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/qino.go -->
# sources/security-integrity/gocryptfs/internal/inomap/qino.go

- Purpose: Defines qualified inode identities consisting of namespace data and inode number, including construction from syscall stat data.
- Important APIs/types/functions: `type namespaceData struct`, `type QIno struct`, `func NewQIno(dev uint64, tag uint8, ino uint64) QIno`, `func QInoFromStat(st *syscall.Stat_t) QIno`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 1067 bytes across 44 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/qino.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/qino.go -->
