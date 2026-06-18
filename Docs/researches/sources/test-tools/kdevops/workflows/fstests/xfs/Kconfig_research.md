## sources/test-tools/kdevops/workflows/fstests/xfs/Kconfig

Purpose: Defines a large XFS fstests coverage model, including xfsprogs/xfsdump build options, quota mount options, CRC/no-CRC, reflink/rmapbt, external log, realtime device, large block size, stripe, nrext64, and bigblock configurations.

Important APIs/types/functions: Distro capability symbols include `HAVE_DISTRO_XFS_SUPPORTS_*` and `HAVE_DISTRO_XFS_IGNORES_NOCRC`. User/config symbols include `FSTESTS_XFS_BUILD_CUSTOM_XFSPROGS`, `FSTESTS_XFS_XFSPROGS_*`, `FSTESTS_XFS_BUILD_XFSDUMP`, `FSTESTS_XFS_QUOTA_ENABLED`, `FSTESTS_XFS_SECTION_*`, and `FSTESTS_XFS_ENABLE_LBS*`.

Control flow: After tool-build and quota options, manual coverage exposes detailed section switches. Nested gates constrain logdev, rtdev, no-CRC, LBS-real, LBS-on-4K-sector, and reflink sections. Non-manual mode supplies a smaller hidden default matrix with CRC, no-CRC, 512-byte no-CRC, reflink, 1K reflink, normapbt, logdev enabled, and bigblock if supported.

State and persistence: Kconfig persists selections into `.config`; Make/Ansible later use them to create hosts and fstests config sections. No direct file writes.

Dependencies and integration points: Sourced by the parent fstests Kconfig when XFS is selected. It depends on architecture/storage capability symbols such as `HAVE_ARCH_64K_PAGES` and `EXTRA_STORAGE_SUPPORTS_*`; tool build options integrate with xfsprogs/xfsdump repositories and mirrors.

Risks and test signals: The matrix is large and easy to desynchronize from actual generated config templates or storage availability. Test by enumerating generated XFS sections, validating mkfs options, and running `oscheck.sh --check-deps` plus dry-run `./check` commands per selected section.
