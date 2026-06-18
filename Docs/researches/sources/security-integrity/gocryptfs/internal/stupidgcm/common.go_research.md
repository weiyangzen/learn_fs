<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/common.go

- Purpose: Implements common OpenSSL AEAD methods for nonce/tag sizing, seal/open dispatch through C helpers, and key wiping state.
- Important APIs/types/functions: `type stupidAEADCommon struct`, `func (c *stupidAEADCommon) Overhead() int`, `func (c *stupidAEADCommon) NonceSize() int`, `func (c *stupidAEADCommon) Seal(dst, iv, in, authData []byte) []byte`, `func (c *stupidAEADCommon) Open(dst, iv, in, authData []byte) ([]byte, error)`, `func (c *stupidAEADCommon) Wipe()`, `func (c *stupidAEADCommon) Wiped() bool`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 1554 bytes across 71 lines, read as part of this work item.
- Dependencies and integration points: standard library: log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/common.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/stupidgcm/common_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common.go -->
