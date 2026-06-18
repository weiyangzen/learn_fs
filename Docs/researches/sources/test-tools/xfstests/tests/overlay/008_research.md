# sources/test-tools/xfstests/tests/overlay/008


Purpose: Tests overlayfs uid/gid ownership when creating files or directories over overlay whiteouts as another user.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_user`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for uid/gid ownership when creating files or directories over overlay whiteouts as another user, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 52 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
