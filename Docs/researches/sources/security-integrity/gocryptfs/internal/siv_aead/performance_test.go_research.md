<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/siv_aead, centered on test cases. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 17 bytes across 2 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Test file with table or scenario assertions but no standard Test declaration was extracted; inspect manually if this changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go -->
