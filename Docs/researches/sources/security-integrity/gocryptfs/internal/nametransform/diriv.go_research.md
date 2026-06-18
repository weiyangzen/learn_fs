<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/diriv.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/diriv.go

- Purpose: Reads and writes per-directory IV files, validating length and all-zero corruption cases.
- Important APIs/types/functions: `const (`, `var allZeroDirIV = make([]byte, DirIVLen)`, `func (n *NameTransform) ReadDirIVAt(dirfd int) (iv []byte, err error)`, `func fdReadDirIV(fd *os.File) (iv []byte, err error)`, `func WriteDirIVAt(dirfd int) error`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state. Source size is 3157 bytes across 99 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, io, os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/diriv.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/diriv.go -->
