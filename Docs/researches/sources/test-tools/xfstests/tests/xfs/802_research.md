<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/802 -->
# sources/test-tools/xfstests/tests/xfs/802

Purpose: end-to-end systemd service coverage for XFS online fsck background scans. It checks per-filesystem `xfs_scrub@` and global `xfs_scrub_all` services and verifies post-scan health reporting.

Important APIs, types, and functions: uses `_require_systemd_is_running`, `_systemd_unit_path`, `_systemd_runtime_dir`, `_xfs_scrub_svcname`, `_scratch_populate_cached`, `xfs_spaceman health`, `attr -R -s xfs:autofsck`, and a local `run_scrub_service` wait loop.

Control flow: the script populates scratch, marks the mount for autofsck, starts the specific scrub service, clones and edits the runtime `xfs_scrub_all.service` to avoid the host media-scan stamp, cycles the mount, and starts the modified global service.

State and persistence behavior: it creates a temporary runtime systemd unit and temporary stamp directory, both cleaned up. Scratch health state and xattrs are changed only for the test filesystem.

Dependencies and integration points: integrates with systemd, python3-dbus for `xfs_scrub_all`, xfs_scrub, xfs_spaceman health, populate helpers, and attr support.

Risks and test signals: marked unreliable in parallel because global scrub scans mounted filesystems. Test signals are successful service completion and `health` output ending in `ok` for scratch.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/802 -->
