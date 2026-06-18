# sources/test-tools/syzkaller/tools/syz-showprio/showprio.go

## Purpose
`syz-showprio` prints a table of syzkaller call-to-call priority values for a specified set of enabled syscalls.

## Important APIs, types, and functions
- Flags select OS/arch, comma-separated enabled calls, and optional corpus file.
- `main` loads target metadata, validates enabled syscalls through `mgrconfig.ParseEnabledSyscalls`, reads corpus, computes priorities with `target.CalculatePriorities`, and calls `showPriorities`.
- `showPriorities` indexes the priority matrix by syscall IDs and prints rows/columns for the requested call names.
- `printLine` prints fixed-width pipe-delimited cells.

## Control flow
The tool fails if `-enable` is empty or invalid. It does not use the parsed syscall IDs directly; it relies on the original names to index `target.SyscallMap`. Corpus-derived priorities are computed for the whole target, then a selected submatrix is printed.

## State and persistence behavior
Reads an optional corpus DB and writes only stdout/stderr. No persistent files are modified.

## Dependencies and integration points
Uses `prog` target priority calculation, `pkg/db` corpus loading, and `pkg/mgrconfig` syscall validation. It is a diagnostic companion for fuzzing choice table behavior.

## Risks and edge cases
Aliases or patterns accepted by `ParseEnabledSyscalls` may not be valid direct keys in `target.SyscallMap`, since `showPriorities` uses the raw `enabled` strings. Empty corpus behavior depends on `db.ReadCorpus`. Output is human-readable rather than CSV/TSV.

## Test signals
No direct tests. Tests should validate a small known target/corpus matrix, invalid syscall names, and behavior with syscall aliases/patterns.
