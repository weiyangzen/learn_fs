# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_linux.go

Purpose: Linux-specific prerequisite checker for the packaging CLI.

Important APIs/types/functions: `checkForTools`.

Control flow: checks `git`, `fpm`, and `go` with `exec.LookPath`, returning distro-oriented install instructions on the first missing tool.

State/persistence behavior: no persistent state.

Dependencies/integration: selected by Go build tags through filename suffix on Linux.

Risks/test signals: checks availability only, not compatible versions of fpm, Go, or build tooling.
