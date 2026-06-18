# sources/test-tools/xfstests/tests/generic/754


Purpose: Regression test that adding/removing xattrs on symlinks of many target lengths does not corrupt symlink targets after remount.


Important APIs, helpers, and commands: Uses `_require_symlinks`, `_scratch_cycle_mount`, `attr -Rs/-Rr`, `readlink`, and XFS-specific `_fixed_by_git_commit` annotations.
 It imports `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_symlinks`.
 Regression annotations include `_fixed_by_git_commit kernel 38de567906d95 \, _fixed_by_git_commit xfsprogs XXXXXXXXXXXXX \`.



Control flow, state, dependencies, risks, and test signals: It creates symlinks with targets growing from 32 to under 1024 bytes, sets and removes three root namespace attrs on each symlink, cycles the mount, then reconstructs expected targets and compares readlink output. State is symlink inode data and any remote/inline target representation on scratch. Dependencies are symlink and attr support. Risks are attr tool availability/permissions and silent attr failures being redirected. Signal is any `target is corrupt` message; otherwise silence. Source size is 61 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
