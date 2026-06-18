# sources/sync-backup/git-lfs/lfs/gitfilter.go

Purpose: small holder for Git LFS clean/smudge operations with configuration, filesystem, and clock dependencies.

Important APIs/types/functions: `GitFilter`, `NewGitFilter`, `ObjectPath`, and `RemoteRef`.

Control flow: constructor pulls filesystem from config and a real clock. `ObjectPath` delegates to the filesystem. `RemoteRef` builds a `git.RefUpdate` from current and push remote config to determine the destination ref for transfer metadata.

State/persistence behavior: no direct writes; methods expose paths and config-derived ref state.

Dependencies/integration: used by clean/smudge files and transfer queue setup.

Risks/test signals: `RemoteRef` depends on current ref and push config being initialized; nil or detached states rely on lower-level git helpers.
