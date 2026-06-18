<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go

Purpose: go-fuzz entrypoint for the Linux mountinfo parser.

Important APIs, types, and functions: under the `gofuzz` build tag, `Fuzz(data []byte) int` calls the package-private `parse` function and returns 1 for valid parsed lines and 0 for rejected inputs.

Control flow: fuzzing feeds arbitrary bytes directly to `parse`; parse errors are non-interesting, successful parses are kept as useful corpus inputs.

State and persistence behavior: no state beyond fuzzer-managed corpus data.

Dependencies and integration points: integrates with `go-fuzz-build` and the `mountinfo` package parser.

Risks and test signals: the useful signal is absence of panics on malformed mountinfo and growth of valid corpus entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go -->
