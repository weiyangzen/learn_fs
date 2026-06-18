## sources/test-tools/kdevops/workflows/fstests/osfiles/debian/helpers.sh

Purpose: Provides Debian-specific hooks for oscheck: OS identification, known expunge lists, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `debian_read_osfile`, `debian_special_expunges`, `debian_skip_groups`, `debian_restart_ypbind`, and `debian_distro_kernel_check`, which are discovered dynamically by `oscheck-lib.sh`.

Control flow: Release-specific cases add xfsprogs or ext4 expunge files. XFS always skips the `encrypt` group. Kernel detection checks `/boot/config-$(uname -r)` for Debian trusted keys.

State and persistence: It mutates shell variables such as `VERSION_ID`, `SKIP_GROUPS`, and `_SKIP_GROUPS`, and appends expunge flags through oscheck library helpers. It writes no files itself.

Dependencies and integration points: Requires `lsb_release`, `/etc/os-release` or equivalent release data, `/boot/config-*`, and oscheck functions such as `oscheck_add_expunge_if_exists`.

Risks and test signals: Debian testing release handling is string-based and can drift. Test by sourcing through `oscheck-get-failures.sh --test-section ...` and confirming expected expunge files and distro-kernel classification.
