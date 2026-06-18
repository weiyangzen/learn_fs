## sources/test-tools/kdevops/workflows/fstests/osfiles/fedora/helpers.sh

Purpose: Supplies Fedora-specific oscheck behavior for release parsing, expunges, XFS skip groups, ypbind restart, and distro-kernel detection.

Important APIs/types/functions: Implements `fedora_read_osfile`, `fedora_special_expunges`, `fedora_skip_groups`, `fedora_restart_ypbind`, and `fedora_distro_kernel_check`.

Control flow: Reads `VERSION_ID` and `PRETTY_NAME` from os-release. Fedora 28 gets broad XFS skip groups and older xfsprogs/y2038 expunges; Fedora 34 gets xfsprogs-maintainer and ext4 xfstests-bld expunges.

State and persistence: Mutates shell state for `VERSION_ID`, `_SKIP_GROUPS`, and expunge flags; no direct persistence.

Dependencies and integration points: Loaded by `oscheck_include_os_files` when `OSCHECK_ID=fedora`. Uses `file /boot/vmlinuz-$(uname -r)` to detect Fedora kernels.

Risks and test signals: Kernel detection depends on the `file` output containing `fedoraproject.org`. Validate on Fedora images by running `oscheck.sh --is-distro` and checking generated skip args.
