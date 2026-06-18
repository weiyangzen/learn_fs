## sources/sync-backup/kopia/fs/localfs/doc.go

Purpose: package documentation declaring `localfs` as the virtual filesystem abstraction over the host local filesystem.

Important APIs/types/functions: no runtime symbols; the package comment is the exported documentation anchor.

Control flow, state, and persistence: none.

Dependencies and integration points: integrates with Go documentation for the `localfs` package, whose implementation maps OS files, directories, symlinks, error entries, and shallow placeholders into Kopia `fs` interfaces.

Risks and test signals: no direct tests required; correctness is tied to package documentation remaining accurate as `localfs` evolves.
