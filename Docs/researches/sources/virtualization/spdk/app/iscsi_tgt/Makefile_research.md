# File Research: sources/virtualization/spdk/app/iscsi_tgt/Makefile

## Purpose
Builds the SPDK iSCSI target application `iscsi_tgt`.

## Main Contents
- Sets `APP = iscsi_tgt`.
- Adds `-I$(SPDK_ROOT_DIR)/lib` because iSCSI lacks a public API header.
- Compiles `iscsi_tgt.c`.
- Links all modules plus `event` and `event_iscsi`.
- Adds `env_dpdk_rpc` for DPDK env builds.
- Adds `event_nbd` on Linux.
- Provides install/uninstall targets.

## Dependencies
Depends on SPDK event framework, iSCSI event subsystem, all configured modules, optional DPDK RPC integration, and optional Linux NBD event support.

## Filesystem/Block Relevance
Builds the SPDK userspace iSCSI target, which exposes SPDK block devices over iSCSI.

## Risks and Notes
- The private include path is explicitly temporary.
- Link set varies by OS and env backend.
