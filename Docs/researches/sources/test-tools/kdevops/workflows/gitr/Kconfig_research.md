## sources/test-tools/kdevops/workflows/gitr/Kconfig

Purpose: Configures the Git regression test workflow and the filesystem under test.

Important APIs/types/functions: Symbols include filesystem choice `GITR_XFS/BTRFS/EXT4/NFS/TMPFS`, `GITR_MNT`, repository selectors `HAVE_MIRROR_GIT`, `GITR_REPO_CUSTOM`, `GITR_REPO_URL`, `GITR_REPO`, `GITR_REPO_COMMIT`, test selectors `GITR_ALL_TESTS`, `GITR_TEST_LIST`, and thread mode symbols.

Control flow: The file selects one filesystem, sources its sub-Kconfig, sets mount path and repository source/ref, and in dedicated workflow mode exposes all-vs-specific tests plus single/fast/stress/custom thread modes.

State and persistence: Kconfig state persists in `.config` and becomes gitr extra vars through Makefile translation.

Dependencies and integration points: Integrates with filesystem-specific subdirectories, libvirt mirror detection, default Git URL constants, and host group generation for dedicated workflows.

Risks and test signals: Default `GITR_REPO_COMMIT` is pinned, so test age must be intentional. Validate selected filesystem args, repository URL/ref, and generated test group lists before running `make gitr-baseline`.
