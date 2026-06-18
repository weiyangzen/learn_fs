<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go

- Purpose: Caches opened directory file descriptors and directory IVs to reduce repeated open/read-diriv work in forward-mode path preparation.
- Important APIs/types/functions: `type dirCacheEntry struct`, `type dirCache struct`, `const (`, `func (e *dirCacheEntry) Clear()`, `func (d *dirCache) Clear()`, `func (d *dirCache) Store(node *Node, fd int, iv []byte)`, `func (d *dirCache) Lookup(node *Node) (fd int, iv []byte)`, `func (d *dirCache) expireThread()`, `func (d *dirCache) stats()`, `func (d *dirCache) dbg(format string, a ...interface`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; treats invalid internal invariants as fatal/panic conditions. Source size is 4388 bytes across 183 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, log, sync, syscall, time; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go -->
