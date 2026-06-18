<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config.go -->
# sources/sync-backup/git-lfs/git/config.go

## Research

`git/config.go` wraps `git config`. `Configuration` stores workdir, gitdir, cached version, read-only flag, and mutex. Constructors support normal and read-only configs. It exposes find/set/unset methods for global, system, local, worktree, and file scopes; parses config output into `ConfigurationSource`; and resolves source ordering for `.lfsconfig` plus normal Git config.

Control flow shells out to `git config --includes`, optionally setting `cmd.Dir` to `GitDir`. `Sources` loads regular config, then safe optional config from working tree, index, or `HEAD`, depending on bare status and file existence. Persistent effects occur only through write methods unless `readOnly` returns `ErrReadOnly`. Dependencies include subprocess execution, Git repository state, and config safety flags consumed by `config.GitFetcher`. Risks include command failures swallowed by `Find*`, read-only bypass if callers use other Git APIs, `.lfsconfig` source precedence, worktree config support, and running commands from `GitDir` instead of worktree. `config_test.go` verifies read-only writes fail.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config.go -->
