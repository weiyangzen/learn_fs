## sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-leap/helpers.sh

Purpose: Implements openSUSE Leap-specific oscheck hooks for release metadata, known expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Exposes dynamically named functions `opensuse-leap_read_osfile`, `opensuse-leap_special_expunges`, `opensuse-leap_skip_groups`, `opensuse-leap_restart_ypbind`, and `opensuse-leap_distro_kernel_check`.

Control flow: `VERSION_ID` cases 15.0 through 15.4 add xfs/ext4 expunges. Older 15.0 skips several XFS risk groups; all XFS runs skip `encrypt`. Kernel detection greps `/boot/config-*` for `CONFIG_SUSE_KERNEL=y`.

State and persistence: Mutates oscheck shell variables and expunge flags. No persistent files are produced.

Dependencies and integration points: Loaded by `oscheck-lib.sh` based on os-release ID. Requires shell support for hyphenated function names as defined in bash; callers use `${OSCHECK_ID}_...` dispatch.

Risks and test signals: Hyphenated function names are bash-specific and would not work under plain POSIX sh. Test by sourcing under bash via `oscheck.sh`, verifying selected expunge files for each Leap release.
