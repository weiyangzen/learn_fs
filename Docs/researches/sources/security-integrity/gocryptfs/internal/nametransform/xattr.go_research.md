<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/xattr.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/xattr.go

- Purpose: Encrypts and decrypts xattr names using a fixed xattr-name IV and validates xattr namespace restrictions.
- Important APIs/types/functions: `var xattrNameIV = []byte("xattr_name_iv_xx")`, `func isValidXattrName(name string) error`, `func (n *NameTransform) EncryptXattrName(plainName string) (cipherName64 string, err error)`, `func (n *NameTransform) DecryptXattrName(cipherName string) (plainName string, err error)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 1493 bytes across 48 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/xattr.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/xattr.go -->
