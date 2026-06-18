<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config.go -->
# sources/sync-backup/git-lfs/config/config.go

## Research

`config.go` is the main Git LFS configuration façade. `Configuration` combines OS environment, delayed Git config, Git command wrapper, repository/worktree discovery, remotes, extensions, filesystem paths, permission masks, and cached author/committer data. Constructors `New`, `NewIn`, and `NewFrom` support real repositories and tests.

Important APIs include transfer/fetch flags, `Remote`, `PushRemote`, remote setters/validators, `Remotes`, `Extensions`, `SortedExtensions`, `HookDir`, `LocalWorkingDir`, `LocalGitDir`, `Filesystem`, git config find/set/unset wrappers, identity/timestamp helpers, and `RepositoryPermissions`. Control flow is lazy and mutex-protected: Git config and git/work dirs load on demand; `.lfsconfig` is read through `git.Configuration.Sources`; remotes/extensions are parsed by `readGitConfig`; filesystem directories are constructed only when requested. Persistent effects include reading Git config/environment, creating LFS/log/tmp directories through `fs.New`, and writing Git config through wrapper methods. Risks include deadlocks around `PushRemote` temporarily unlocking to call `Remote`, cached stale config, nil `c.fs` in `Cleanup`, Git date parsing compatibility, unsafe `.lfsconfig` filtering, and platform-specific umask behavior. `config_test.go` covers remote precedence, transfer booleans, extension loading, fetch path cleanup, permissions, identity, timestamps, and dotted remote names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config.go -->
