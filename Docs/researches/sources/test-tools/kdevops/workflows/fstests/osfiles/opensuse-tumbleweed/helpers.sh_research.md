## sources/test-tools/kdevops/workflows/fstests/osfiles/opensuse-tumbleweed/helpers.sh

Purpose: Provides openSUSE Tumbleweed oscheck hooks for rolling release expunges, skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `opensuse-tumbleweed_read_osfile`, `_special_expunges`, `_skip_groups`, `_restart_ypbind`, and `_distro_kernel_check` variants.

Control flow: Groups release IDs by year patterns. 2019 releases get broader XFS expunges and skip groups; 2020/2021 add xfsprogs-maintainer and ext4 xfstests-bld expunges. Distro kernel detection uses `CONFIG_SUSE_KERNEL=y`.

State and persistence: Updates shell variables and expunge flag lists; no persistent writes.

Dependencies and integration points: Integrated through dynamic oscheck dispatch. Uses os-release, `/boot/config-*`, and the common `oscheck_systemctl_restart_ypbind` helper.

Risks and test signals: Date-pattern release matching can become stale for newer Tumbleweed snapshots. Test by running with a current Tumbleweed `VERSION_ID` and checking whether intended expunges still apply.
