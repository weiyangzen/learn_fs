<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/names_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestPad16, TestUnpad16Garbage, TestIsValidName, TestIsValidXattrName. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestPad16(t *testing.T)`, `func TestUnpad16Garbage(t *testing.T)`, `func TestIsValidName(t *testing.T)`, `func TestIsValidXattrName(t *testing.T)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names; is non-persistent test/benchmark code. Source size is 2103 bytes across 101 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, strings, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/names_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestPad16, TestUnpad16Garbage, TestIsValidName, TestIsValidXattrName.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names_test.go -->
