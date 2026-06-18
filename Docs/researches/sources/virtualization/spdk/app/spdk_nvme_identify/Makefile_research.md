# File Research: sources/virtualization/spdk/app/spdk_nvme_identify/Makefile

## Purpose
Builds `spdk_nvme_identify`, SPDK's NVMe controller/namespace inspection utility.

## Main Contents
- Sets `APP = spdk_nvme_identify`.
- Compiles `identify.c`.
- Links socket modules, NVMe, and VMD.
- Uses SPDK app make infrastructure and install/uninstall helpers.

## Dependencies
Depends on SPDK NVMe, VMD, socket modules, and common app build fragments.

## Filesystem/Block Relevance
Builds a utility used to inspect NVMe block namespace properties, capabilities, log pages, ZNS state, OCSSD geometry, and FDP data.

## Risks and Notes
- Feature availability depends on controller capabilities and transport.
