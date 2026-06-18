<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go

Purpose: records fuzzing tools as Go module tool dependencies without building them normally.

Important APIs, types, and functions: under the `tools` build tag, blank-imports `github.com/dvyukov/go-fuzz/go-fuzz` and `go-fuzz-build`.

Control flow: no runtime control flow; the file exists for dependency retention.

State and persistence behavior: no program state.

Dependencies and integration points: integrates with Go modules and the local `fuzz` script.

Risks and test signals: if tool module paths change, fuzz setup breaks; normal builds ignore this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go -->
