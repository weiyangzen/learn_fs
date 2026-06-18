# sources/test-tools/xfstests/tests/generic/783


Purpose: Tests overlayfs mount and lookup error cases when underlying layers are casefold-capable or casefold-enabled with matching, strict, or inconsistent encodings.


Important APIs, helpers, and commands: Imports `common/casefold`; defines `mount_casefold_version`, `mount_overlay`, and `unmount_overlay`; uses `_scratch_mkfs_casefold*`, `_casefold_set_attr`, `_casefold_unset_attr`, tmpfs `casefold=` mounts, and overlay mount options.
 Local helper functions detected in the file include `_cleanup`, `mount_casefold_version`, `mount_overlay`, `unmount_overlay`.
 It imports `./common/casefold`, `./common/filter`, `./common/preamble`.
 Capability gates include `_require_extra_fs`, `_require_scratch_casefold`.



Control flow, state, dependencies, risks, and test signals: The test creates casefold-capable scratch layers, probes whether overlay supports enabled layers, then exercises disabled/enabled transitions before/after mount, lower subdir mismatches, upper/work enabled failures, strict encoding cases, and mismatched UTF-8 versions. State is casefold directory attributes, overlay mount state, and temp mountpoints. Dependencies are overlayfs, casefold filesystem support, tmpfs casefold versions, and extra overlay fs availability. Risks are kernel-version-dependent expected skips and mount error wording. Signals are filtered ls/mount failures for ESTALE/EREMOTE/EINVAL scenarios. Source size is 242 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
