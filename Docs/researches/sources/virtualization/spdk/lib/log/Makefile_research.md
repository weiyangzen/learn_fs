# File Research: sources/virtualization/spdk/lib/log/Makefile

Builds SPDK's `log` library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 9`, `SO_MINOR := 1`, and `SO_SUFFIX := $(SO_VER).$(SO_MINOR)`.
- Builds `log.c`, `log_flags.c`, and `log_deprecated.c` into `LIBNAME = log`.
- Adds `-Wpointer-arith` to `CFLAGS`.
- Uses `spdk_log.map` as the export map and includes `mk/spdk.lib.mk`.

Filesystem/block relevance:
- Logging is cross-cutting infrastructure used by SPDK storage subsystems for diagnostics, runtime control-plane visibility, and deprecation reporting.
