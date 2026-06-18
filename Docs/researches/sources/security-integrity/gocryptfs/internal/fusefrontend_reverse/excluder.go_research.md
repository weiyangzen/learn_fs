<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go

- Purpose: Builds reverse-mode exclusion matchers from direct patterns and pattern files, normalizing root-relative excludes.
- Important APIs/types/functions: `func prepareExcluder(args fusefrontend.Args) *ignore.GitIgnore`, `func getExclusionPatterns(args fusefrontend.Args) []string`, `func getLines(file string) ([]string, error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 1686 bytes across 58 lines, read as part of this work item.
- Dependencies and integration points: standard library: log, os, strings; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/exitcodes, github.com/rfjakob/gocryptfs/v2/internal/fusefrontend, github.com/rfjakob/gocryptfs/v2/internal/tlog, github.com/sabhiram/go-gitignore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go -->
