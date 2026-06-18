# File Research: sources/virtualization/spdk/app/Makefile

## Purpose
Top-level SPDK application makefile. It selects which application subdirectories participate in `all` and `clean` builds and delegates recursive build behavior to SPDK's shared make infrastructure.

## Main Contents
- Sets `SPDK_ROOT_DIR` to the parent of `app`.
- Includes `mk/spdk.common.mk`.
- Adds app directories such as `trace`, `nvmf_tgt`, `iscsi_tgt`, `spdk_tgt`, `spdk_lspci`, NVMe tools, and optional apps.
- Omits `spdk_top` on Windows because curses is unsupported there.
- Adds `vhost` only when `CONFIG_VHOST` is enabled.
- Adds `spdk_dd` only on Linux.
- Adds `fio` only when `CONFIG_FIO_PLUGIN` is enabled.
- Includes `mk/spdk.subdirs.mk` for recursive targets.

## Dependencies
Depends on SPDK make variables from `spdk.common.mk`, especially `OS`, `CONFIG_VHOST`, and `CONFIG_FIO_PLUGIN`.

## Filesystem/Block Relevance
This makefile controls whether block-facing apps and tools such as NVMe-oF target, iSCSI target, fio plugins, `spdk_dd`, and NVMe inspection utilities are built.

## Risks and Notes
- Platform gating means some tools are intentionally absent from Windows or non-Linux builds.
- Actual compilation/link details live in each child makefile and SPDK shared make fragments.
