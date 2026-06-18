<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go -->
# sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go

- Purpose: Derives deterministic IV material from paths for reverse mode file content, block IVs, directory IVs, symlinks, and xattrs.
- Important APIs/types/functions: `type Purpose string`, `type FileIVs struct`, `const (`, `func Derive(path string, purpose Purpose) []byte`, `func DeriveFile(path string) (fileIVs FileIVs)`, `func BlockIV(block0iv []byte, blockNo uint64) []byte`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 1892 bytes across 60 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/sha256, encoding/binary; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/nametransform. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go -->
