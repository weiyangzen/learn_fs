## sources/test-tools/kdevops/workflows/fstests/tmpfs/Kconfig

Purpose: Defines tmpfs fstests coverage sections for default mounts, noswap mode, and huge-page mount policies.

Important APIs/types/functions: Symbols include `FSTESTS_TMPFS_MANUAL_COVERAGE`, `FSTESTS_TMPFS_SECTION_DEFAULT`, `FSTESTS_TMPFS_ENABLE_NOSWAP`, `FSTESTS_TMPFS_SECTION_NOSWAP_HUGE_*`, `FSTESTS_TMPFS_ENABLE_HUGE`, and `FSTESTS_TMPFS_SECTION_HUGE_*`.

Control flow: Manual mode exposes default, noswap, and huge-page section selections. Non-manual mode defaults only the default section and leaves other hidden selectors unset.

State and persistence: Selections persist in `.config` and are converted to Make/Ansible args by the tmpfs Makefile.

Dependencies and integration points: Sourced by parent fstests Kconfig for tmpfs. Downstream inventory/host config generation must map selected symbols to tmpfs mount options such as huge modes and swap behavior.

Risks and test signals: Huge-page behavior depends on kernel and system THP settings, not only mount options. Verify generated tmpfs section configs and target runtime mount options.
