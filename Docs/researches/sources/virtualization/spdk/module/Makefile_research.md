# File Research: sources/virtualization/spdk/module/Makefile

## Purpose

Top-level SPDK module build Makefile. It selects module subdirectories and generates module/system pkg-config files.

## Key Contents

- Sets `SPDK_ROOT_DIR` and includes common/module make fragments.
- Always builds core module directories: `bdev blob accel event sock scheduler keyring`.
- Conditionally adds:
  - `env_dpdk` when `CONFIG_ENV` is DPDK env.
  - `fsdev` when `CONFIG_FSDEV=y`.
  - `vfu_device` when `CONFIG_VFIO_USER=y`.
- Defines dependency ordering between module subdirs.
- Generates pkg-config files for bdev, accel, sock, scheduler, keyring, and syslibs.
- Filters build-tree `-L` paths from installed syslibs and replaces them with install libdir.

## Relationships

- `module/accel/Makefile` is one of the subdirectories reached through `DIRS-y`.
- Uses `scripts/pc_modules.sh` and `scripts/pc_libs.sh`.
- Installs/uninstalls generated pkg-config artifacts.

## Notes

- Build composition is driven by config variables from SPDK make infrastructure.
