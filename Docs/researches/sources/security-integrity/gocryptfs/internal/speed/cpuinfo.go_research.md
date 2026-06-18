<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go -->
# sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go

- Purpose: Extracts a Linux CPU model string for speed benchmark reporting, with runtime fallback on non-Linux systems.
- Important APIs/types/functions: `func cpuModelName() string`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 1112 bytes across 55 lines, read as part of this work item.
- Dependencies and integration points: standard library: io, os, runtime, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go -->
