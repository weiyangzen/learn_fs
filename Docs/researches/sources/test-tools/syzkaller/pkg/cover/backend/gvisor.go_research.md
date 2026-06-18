# sources/test-tools/syzkaller/pkg/cover/backend/gvisor.go

Purpose: implements a non-DWARF backend for gVisor/runsc coverage. gVisor can emit its own `symbolize -all` output, so this backend converts that stream directly into frames and compile units.

Important APIs/types/functions: `makeGvisor`, `gvisorSymbolize`, `gvisorParseLine`, and `gvisorLineRe`. The backend returns `Impl{Units, Frames}` without callback points or lazy symbolization.

Control flow: `makeGvisor` rejects modules, locates `vmlinux` or fallback `runsc`, runs `gvisorSymbolize`, groups frames by source file into compile units, and returns the implementation. `gvisorSymbolize` starts the binary with `symbolize -all`, scans alternating PC and source-location lines, resolves paths under source dir, and attempts a Bazel generated-file fallback. `gvisorParseLine` parses one PC plus one location line into a backend `Frame`.

State and persistence: transient process execution and in-memory frame/unit slices only.

Dependencies and integration: uses `osutil.Command`, syzkaller target/kernel dirs, and `backend.Impl`. It integrates with `pkg/cover` via the same `Impl` shape but bypasses callback verification.

Risks: process cleanup uses deferred `Wait` and `Kill`; scanner token limits may matter on pathological output. Regex only accepts `pkg/...` paths. Generated files under hashed Bazel output paths are only partially recoverable.

Test signals: `gvisor_test.go` parses real saved symbolize outputs and verifies regex extraction for normal, Bazel, and relative paths.
