# File Research: sources/virtualization/spdk/module/fsdev/Makefile

Top-level build dispatcher for fsdev modules.

Key elements:
- Includes `aio` subdirectory only when `CONFIG_AIO_FSDEV=y`.
- Defines `all` and `clean` phony targets.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Delegates actual AIO fsdev library build to `module/fsdev/aio/Makefile`.

Research notes:
- fsdev module availability is compile-time configurable.
