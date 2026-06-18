# sources/test-tools/syzkaller/dashboard/config/android/generate.sh

Purpose: generates an Android kernel config file from an Android kernel checkout, currently supporting kernel version `5.4`.

Important APIs and commands: Bash script with `usage`, arguments `SRC_DIR` and `VERSION`, variables `KERNEL_SOURCE`, `DEFCONFIG`, `SCRIPT_DIR`, `CC`, sourced `../util.sh`, and helper calls `util_add_usb_bits` and `util_add_syzbot_bits`.

Control flow: validates that the Android GKI defconfig exists, selects a prebuilt clang path for `5.4`, sources shared config utility functions, copies `gki_defconfig` to `.config`, adds Android USB and syzbot config fragments, merges `config-bits` with `scripts/kconfig/merge_config.sh -m`, runs `make olddefconfig`, and copies the resulting `.config` to `config-5.4`.

State and persistence: writes into the Android kernel source tree `.config` and the dashboard config directory output file. It also depends on mutable environment from `util.sh` such as `MAKE_VARS`.

Dependencies and integration points: Android kernel source layout with `common`, prebuilts clang path for 5.4, Linux kernel kconfig scripts, make, and dashboard config utility scripts/fragments. Intended for maintainers refreshing checked-in Android kernel configs.

Risks: hard-coded compiler path and single supported version make it fragile for newer Android branches. `set -eux` is useful for fail-fast but can expose paths/commands in logs. Arguments are not quoted consistently around `cd`, `cp`, and script paths, so spaces in checkout paths would break. It overwrites `.config` in the kernel tree.

Test signals: no automated test in this subset. Successful run producing `config-5.4` after `olddefconfig` is the practical validation.
