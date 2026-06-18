<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go

- Purpose: Contains reverse-mode block encryption and backing plaintext read helpers, including deterministic per-path IV/file-ID derivation.
- Important APIs/types/functions: `var inodeTable sync.Map`, `func (rf *File) encryptBlocks(plaintext []byte, firstBlockNo uint64, fileID []byte, block0IV []byte) []byte`, `func (f *File) readBackingFile(off uint64, length uint64) (out []byte, err error)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 2010 bytes across 63 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, io, sync; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go -->
