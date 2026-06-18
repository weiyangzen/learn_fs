<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/access.go -->
# sources/sync-backup/git-lfs/creds/access.go

## Research

`access.go` defines authentication access modes and the `Access` value object. Modes include `none`, `basic`, `private`, `negotiate`, and empty. `NewAccess` constructs an access descriptor, `Upgrade` returns a copy with a new mode while preserving URL, and getters expose mode and URL. `AllAccessModes` returns the order attempted: none, negotiate, basic.

There is no persistence or I/O. Integration is with LFS API authentication negotiation and credential helper selection. Risks are policy-related: `PrivateAccess` and `EmptyAccess` are not returned by `AllAccessModes`, so callers must handle them separately, and adding a new mode requires updating negotiation order consistently.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/access.go -->
