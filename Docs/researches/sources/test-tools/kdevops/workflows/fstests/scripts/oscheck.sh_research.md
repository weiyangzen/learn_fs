## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck.sh

Purpose: OS wrapper around fstests `check.sh` that validates dependencies, devices, distro policy, expunges, and then runs `./check` with the correct section and exclusions.

Important APIs/types/functions: Key functions are `parse_args`, `oscheck_get_progs_version`, `check_services`, `check_reqs`, `check_mount`, `oscheck_run_section`, `_check_dev_setup`, `oscheck_test_dev_setup`, `check_kernel_config`, `check_test_dev_setup`, and `check_dev_pool`.

Control flow: The script requires root, parses wrapper and passthrough args, resolves the run section and host config, unmounts an already-mounted test dir, loads OS helper policy, applies skip groups, checks users/groups/directories/tools/services, validates the fstests tree and kernel config, validates devices/pools, optionally exits after dependency checks, gathers tool versions, formats/mount-checks devices, computes expunges, and finally runs `LC_ALL=C bash ./check ...`.

State and persistence: It may create users/groups/directories when `FSTESTS_SETUP_SYSTEM=y`, format block devices, mount/unmount test devices, write `/tmp/run-cmd.txt`, and optionally emit journal output through `systemd-cat`. It inherits and exports substantial shell state from oscheck-lib.

Dependencies and integration points: Requires fstests tree, root privileges, mkfs tools, user/group management tools, systemd/ypbind when relevant, host config files, expunge files, and the oscheck library. Kdevops uses it inside fstests workflows to normalize per-distro execution.

Risks and test signals: It can alter system users/groups and filesystems, so dry-run and dependency-only modes are important. Test signals include `--check-deps`, `-n --show-cmd`, `--expunge-list`, root/non-root behavior, and a smoke run against a disposable test device.
