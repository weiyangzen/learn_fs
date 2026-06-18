# sources/test-tools/xfstests/tests/overlay/005


Purpose: Tests overlayfs copy-up ENOSPC error handling using separate loop-mounted lower and small upper XFS filesystems.


Important APIs, helpers, and commands: Uses xfstests overlay scratch helpers, `common/filter`, feature gates such as `_require_scratch`, `_require_scratch_feature`, `_require_scratch_overlay_features`, and command-specific helpers depending on the case.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_loop`, `_require_scratch_nocheck`.



Control flow, state, dependencies, risks, and test signals: The script prepares lower/upper/work directories, mounts overlay with the feature options required by the case, performs the operation sequence for copy-up ENOSPC error handling using separate loop-mounted lower and small upper XFS filesystems, often unmounts or cycles the mount to force cache/index revalidation, and checks visible output through filters or helper tools. State is overlay layer contents, whiteouts, xattrs, index/origin metadata, copied-up files, and mount/cache state. Dependencies are overlayfs plus the specific feature under test such as index, redirect_dir, nfs_export, trusted xattrs, chattr, flock, fsck.overlay, or open_by_handle. Risks include direct offline edits to layer directories, feature-specific mount failures, root-only operations, and output sensitivity around inode numbers. Test signals are filtered command output, absence of warnings/oops, fsck status expectations, stable inode/nlink values, or helper success. Source size is 91 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
