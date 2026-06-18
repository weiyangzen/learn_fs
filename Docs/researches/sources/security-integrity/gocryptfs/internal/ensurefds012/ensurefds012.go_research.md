<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go -->
# sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go

- Purpose: Runs at package initialization to guarantee file descriptors 0, 1, and 2 are open by duplicating /dev/null if necessary.
- Important APIs/types/functions: `func init()`.
- Control flow and state: can terminate the process on unrecoverable setup or external command errors. Source size is 1461 bytes across 52 lines, read as part of this work item.
- Dependencies and integration points: standard library: os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/exitcodes. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go -->
