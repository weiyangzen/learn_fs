<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile

- Purpose: Build/test helper for the package, checking multiple OpenSSL and without-OpenSSL build modes plus C compiler warning coverage.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 452 bytes across 19 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile -->
