# File Research: sources/local-fs/erofs-utils/lib/liberofs_rebuild.h

This header declares rebuild/merge support for constructing a target tree from existing EROFS trees and tar/container-like paths.

Data mode enum:
- `EROFS_REBUILD_DATA_BLOB_INDEX`: represent source data through blob chunk indexes.
- `EROFS_REBUILD_DATA_RESVSP`: reserve data space.
- `EROFS_REBUILD_DATA_FULL`: declared, but the implementation in this group does not support it for regular files.

API:
- `erofs_rebuild_get_dentry()` resolves/creates a path under an in-memory directory tree, with AUFS whiteout and opaque-directory detection.
- `erofs_rebuild_load_tree()` loads an existing source EROFS tree into a target root using a selected data mode.
- `erofs_rebuild_load_basedir()` loads entries from a base directory for incremental rebuilds.

Known implementation:
- `rebuild.c`.

Risk / note:
- `erofs_rebuild_get_dentry()` mutates the path buffer while splitting components, so callers must pass writable storage.
