# File Research: sources/os/plan9/9front/sys/src/cmd/git/compat

Compatibility wrapper that emulates selected mainstream `git` commands using 9front git commands.

Key responsibilities:
- Implements dispatch functions for init, clone, pull/fetch, checkout, submodule, rev-parse, show-ref, remote add, log/show, ls-remote, version, and status.
- Handles common flags used by tools such as Go.
- Can bind itself as `git` in a temporary namespace when invoked as `compat`.
- Locates repo root for commands that need it.

Important behavior:
- Reports version as `git version 2.2.0`.
- Submodules are explicitly unsupported if `.gitmodules` exists.
- Debug mode logs commands to `/tmp/gitlog`.

Notable risks:
- Contains two `cmd_rev-parse` definitions; the later one overrides the earlier in rc function namespace.
- `cmd_checkout` calls `git/branch $b`, but `b` is not set in that function.
