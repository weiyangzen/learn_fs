<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/longnames.go

- Purpose: Implements long filename hashing, sidecar naming, sidecar reads/deletes/writes, and long-name classification.
- Important APIs/types/functions: `const (`, `const (`, `func (n *NameTransform) HashLongName(name string) string`, `func NameType(cName string) int`, `func IsLongContent(cName string) bool`, `func RemoveLongNameSuffix(cName string) string`, `func ReadLongNameAt(dirfd int, cName string) (string, error)`, `func DeleteLongNameAt(dirfd int, hashName string) error`, `func (n *NameTransform) WriteLongNameAt(dirfd int, hashName string, plainName string) (err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 5183 bytes across 169 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/sha256, fmt, io, os, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/longnames.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames.go -->
