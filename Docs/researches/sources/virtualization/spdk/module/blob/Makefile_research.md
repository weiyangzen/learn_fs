# File Research: sources/virtualization/spdk/module/blob/Makefile

Top-level build dispatcher for SPDK blob modules.

Key elements:
- Sets `SPDK_ROOT_DIR` two levels up.
- Includes `mk/spdk.common.mk`.
- Builds only the `bdev` subdirectory through `DIRS-y = bdev`.
- Uses `spdk.subdirs.mk` for `all` and `clean`.

Dependencies:
- Delegates actual library build to `module/blob/bdev/Makefile`.

Research notes:
- This file is directory orchestration only; no C sources are compiled here directly.
