# sources/test-tools/syzkaller/docs/docs.go Research

## Purpose
Package `docs` exposes selected Markdown documentation as embedded strings for LLM-oriented agent flows in `pkg/aflow`.

## Important APIs
- `ProgramSyntax string` embeds `program_syntax.md`.
- `SyscallDescriptionsSyntax string` embeds `syscall_descriptions_syntax.md`.
- Uses Go `//go:embed` with a blank import of `embed`.

## Control flow
There is no runtime control flow beyond compile-time embedding. Importers read the exported string variables directly.

## State and persistence
The embedded content is fixed at build time. Changes to the Markdown files require rebuilding downstream binaries to update the strings.

## Dependencies and integration points
Depends on the Go embed toolchain and the two Markdown files existing in the same package directory. Integrates with `pkg/aflow` consumers that need prompt/reference text.

## Risks
Missing embedded files break compilation. Large documentation changes can affect binary size and prompt behavior.

## Test signals
Go build of the package verifies embed paths. Unit tests for aflow prompt construction would catch accidental empty or stale content; no Go tests were run in this pass.
