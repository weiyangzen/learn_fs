<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz

Purpose: helper shell script for running go-fuzz against the `mountinfo` parser.

Important APIs, types, and functions: runs `go-fuzz-build` and then `go-fuzz -workdir=testdata/fuzz` via `go run github.com/dvyukov/go-fuzz/...`.

Control flow: `set -e` stops on build errors; successful build immediately execs the fuzzing loop.

State and persistence behavior: fuzz corpus, crashers, and generated artifacts live under `testdata/fuzz`.

Dependencies and integration points: depends on the go-fuzz tooling and the build-tagged `fuzz.go` entrypoint.

Risks and test signals: external tool availability and corpus quality drive coverage. Crashes become regression tests through the corpus files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz -->
