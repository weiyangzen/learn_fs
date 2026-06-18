# File Research: sources/virtualization/spdk/lib/conf/Makefile

Builds the SPDK `conf` shared/static library from `conf.c`. It sets the library ABI version to `8.0`, points at `spdk_conf.map`, includes common SPDK make rules, and delegates actual library build mechanics to `mk/spdk.lib.mk`.
