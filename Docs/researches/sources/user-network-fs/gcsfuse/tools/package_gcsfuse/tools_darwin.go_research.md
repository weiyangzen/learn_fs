# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_darwin.go

Purpose: Darwin-specific prerequisite checker for the packaging CLI.

Important APIs/types/functions: `checkForTools`.

Control flow: checks `git`, `fpm`, and `go` with `exec.LookPath`, returning an install-instruction error on the first missing tool.

State/persistence behavior: no persistent state.

Dependencies/integration: selected by Go build tags through filename suffix on macOS.

Risks/test signals: the fpm instruction includes installing gnu-tar and fpm through gem; no version pinning is enforced.
