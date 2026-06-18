<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed.go -->
# sources/security-integrity/gocryptfs/internal/speed/speed.go

- Purpose: Runs comparative AEAD benchmarks for OpenSSL/Go AES-GCM, AES-SIV, XChaCha20-Poly1305, and block-size variants.
- Important APIs/types/functions: `const adLen = 24`, `const gocryptfsBlockSize = 4096`, `func Run()`, `func mbPerSec(r testing.BenchmarkResult) float64`, `func randBytes(n int) []byte`, `func bEncrypt(b *testing.B, c cipher.AEAD)`, `func bEncryptBlockSize(b *testing.B, c cipher.AEAD, blockSize int)`, `func bDecrypt(b *testing.B, c cipher.AEAD)`, `func bStupidGCM(b *testing.B)`, `func bGoGCM(b *testing.B)`, `func bGoGCMBlockSize(b *testing.B, blockSize int)`, `func bAESSIV(b *testing.B)` (2 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4554 bytes across 171 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, crypto/cipher, crypto/rand, fmt, log, testing; external/internal modules: golang.org/x/crypto/chacha20poly1305, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/siv_aead, github.com/rfjakob/gocryptfs/v2/internal/stupidgcm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/speed.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/speed/speed_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed.go -->
