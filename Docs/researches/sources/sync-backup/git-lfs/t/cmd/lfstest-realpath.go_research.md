# sources/sync-backup/git-lfs/t/cmd/lfstest-realpath.go

Purpose: canonicalizes a path similarly to `realpath`, while tolerating missing trailing components.

Important functions: `canonicalize` and `main`.

Control flow: converts the argument to an absolute path, then repeatedly tries `filepath.EvalSymlinks` on the existing left side. If a component is missing, it walks left upward and accumulates the unresolved suffix on the right until an existing prefix can be canonicalized, then rejoins.

State/persistence behavior: read-only filesystem metadata inspection.

Dependencies/integration: shell tests use it for symlink/canonical path comparisons where the final path may not exist yet.

Risks: loop correctness depends on eventually finding an existing ancestor. Permission errors abort, while nonexistence is tolerated.

Test signals: stdout canonical absolute path and exit codes for bad usage/abs/canonicalization failures.
