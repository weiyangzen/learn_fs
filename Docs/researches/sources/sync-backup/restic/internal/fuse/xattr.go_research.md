## sources/sync-backup/restic/internal/fuse/xattr.go

Purpose: shared helpers for exposing stored extended attributes through FUSE.

Important APIs: `nodeToXattrList` appends each `data.Node.ExtendedAttributes` name to a `fuse.ListxattrResponse`. `nodeGetXattr` uses `node.GetExtendedAttribute` and sets `resp.Xattr`, returning `fuse.ErrNoXattr` when absent.

Control flow and state: helpers are stateless and directly reflect metadata stored in `data.Node`. They log attribute operations for debug builds.

Dependencies and integration points: used by file, directory, and symlink FUSE nodes. Depends on `anacrolix/fuse`, `data.Node`, and restic debug logging.

Risks and test signals: response sizing is delegated to the FUSE response API. Missing xattrs must map to the platform FUSE error, which `TestLink` covers for symlinks; other node types rely on shared helper behavior.
