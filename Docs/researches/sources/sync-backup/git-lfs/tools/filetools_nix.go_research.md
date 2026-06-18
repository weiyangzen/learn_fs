# sources/sync-backup/git-lfs/tools/filetools_nix.go

Purpose: non-Windows implementation of `CanonicalizeSystemPath`.

Important APIs/types/functions: `CanonicalizeSystemPath(path string) (string, error)`.

Control flow: converts input to an absolute path with `filepath.Abs`, then resolves symlinks with `filepath.EvalSymlinks`.

State and persistence: read-only filesystem metadata access; no persistent state.

Dependencies and integration points: used by `ResolveSymlinks` and `CanonicalizePath` in `filetools.go` on Unix-like builds.

Risks: missing paths return an error from `EvalSymlinks`; callers needing missing-path tolerance must use `CanonicalizePath(..., true)`.

Test signals: indirectly covered by canonicalization callers; no dedicated nix-only test in this subset.
