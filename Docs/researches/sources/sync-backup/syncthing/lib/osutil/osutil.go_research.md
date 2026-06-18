## sources/sync-backup/syncthing/lib/osutil/osutil.go

Purpose: native OS file operation utilities for robust rename/copy, target preparation, deletion detection, and directory size calculation.

Important APIs: `RenameOrCopy`, `Copy`, `withPreparedTarget`, `copyFileContents`, `IsDeleted`, and `DirSize`. Package-level `renameLock` serializes rename/copy target preparation.

Control flow and state: `RenameOrCopy` locks, attempts rename when source and destination filesystems match, falls back to copy on failure, and removes source after successful copy. `Copy` also locks and delegates to `withPreparedTarget`. `withPreparedTarget` removes existing target files or directory trees and temporarily grants parent directory write permission through `fs.InWritableDir`. `copyFileContents` opens source and destination, uses the filesystem `CopyRangeMethod`, syncs and closes with deferred error propagation. `IsDeleted` stats a path and returns true only for not-exist. `DirSize` walks a real OS directory and sums non-directory sizes.

Persistence behavior: copy writes destination with source mode, syncs destination file, and removes source only after copy success. Directory operations are best-effort around permissions through `InWritableDir`.

Dependencies and integration points: relies on Syncthing `fs.Filesystem` abstractions and is used by model/puller code for final placement and conflict handling.

Risks: rename/copy is serialized globally, which avoids races but can become a bottleneck. Cross-filesystem rename behavior depends on the filesystem implementation returning errors. Removing existing targets before copy means a later copy failure can leave no destination. Directory size ignores walk errors beyond returning zero for inaccessible trees.

Test signals: `osutil_test.go` covers deletion detection, rename/copy, and IP parsing.
