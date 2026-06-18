<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash

- Purpose: Small benchmark wrapper script that runs the package benchmark from the correct directory and delegates to the shared benchmark entry point.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is non-persistent test/benchmark code. Source size is 50 bytes across 4 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash -->
