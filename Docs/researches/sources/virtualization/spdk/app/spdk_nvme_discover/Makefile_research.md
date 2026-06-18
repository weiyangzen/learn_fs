# File Research: sources/virtualization/spdk/app/spdk_nvme_discover/Makefile

## Purpose
Builds `spdk_nvme_discover`, an NVMe-oF discovery utility focused on discovery log changes/AERs.

## Main Contents
- Sets `APP = spdk_nvme_discover`.
- Compiles `discovery_aer.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, socket modules, VMD, and SPDK app make rules.

## Filesystem/Block Relevance
Builds a utility for discovering NVMe-oF subsystems that may expose remote block namespaces.

## Risks and Notes
- The source file is a standalone env-based utility, not a full SPDK event app.
