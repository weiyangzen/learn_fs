<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/fusefrontend, centered on TestEncryptDecryptXattrName. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func newTestFS(args Args) *RootNode`, `func TestEncryptDecryptXattrName(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 1224 bytes across 46 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing, time; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/nametransform. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestEncryptDecryptXattrName.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go -->
