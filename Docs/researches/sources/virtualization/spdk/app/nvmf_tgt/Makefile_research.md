# File Research: sources/virtualization/spdk/app/nvmf_tgt/Makefile

## Purpose
Builds the SPDK NVMe-oF target application `nvmf_tgt`.

## Main Contents
- Sets `APP = nvmf_tgt`.
- Compiles `nvmf_main.c`.
- Links all modules plus `event` and `event_nvmf`.
- Adds `env_dpdk_rpc` for DPDK env builds.
- Adds `event_nbd` on Linux.
- Provides install/uninstall targets.

## Dependencies
Depends on SPDK event framework, NVMe-oF event subsystem, configured modules, optional DPDK RPC, and optional Linux NBD event support.

## Filesystem/Block Relevance
Builds the SPDK userspace NVMe-oF target, exposing SPDK bdevs as NVMe namespaces over fabrics transports.

## Risks and Notes
- Runtime target configuration is supplied through SPDK app/RPC mechanisms rather than this makefile.
