## sources/test-tools/kdevops/workflows/fstests/osfiles/sles/helpers.sh

Purpose: Adds SLES-specific oscheck policy for known fstests failures, skip groups, ypbind restart, and distro-kernel verification.

Important APIs/types/functions: Implements `sles_read_osfile`, `sles_special_expunges`, `sles_skip_groups`, `sles_restart_ypbind`, and `sles_distro_kernel_check`.

Control flow: Release cases for 15.2 through 15.4 add XFS and ext4 expunges. SLES 15.2 also skips older-risk XFS groups, and all XFS runs skip `encrypt`.

State and persistence: Mutates `_SKIP_GROUPS`, `SKIP_GROUPS`, `VERSION_ID`, and expunge flags. It does not write files.

Dependencies and integration points: Loaded by oscheck via `OSCHECK_ID=sles`; uses `/boot/config-$(uname -r)` and `CONFIG_SUSE_KERNEL=y`.

Risks and test signals: `sles_restart_ypbind` only handles 15.0 while expunge cases target later releases; ypbind recovery may fail silently on current images. Test with `oscheck.sh --check-deps` and NIS-active systems.
