# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_adapters.h

## Purpose

`emlxs_adapters.h` defines the Emulex/ATTO adapter identity database: adapter model enum values, PCI vendor/device/subsystem IDs, JEDEC IDs, chip capability flags, model descriptors, firmware IDs, interrupt limits, SLI support, channel counts, and conditional static model tables.

## Main Types

`emlxs_adapter_t` enumerates supported adapter models across generations: DragonFly, Centaur, Pegasus, Thor, Helios, Zephyr, Hornet, Saturn, BE2/BE3/BE4, Lancer FC/FCoE Gen5/Gen6, ATTO Celerity, and Prism Gen7 FC, plus Oracle-branded and excluded variants.

`emlxs_model_t` describes one model: adapter ID, PCI IDs, model strings, manufacturer, feature flags, chip family, firmware ID, interrupt limits, SLI mask, channel count, and program-type byte arrays for firmware/boot/SLI images.

## Constants and Tables

Vendor IDs include Emulex, ATTO, and OCE. Subsystem vendor IDs include Emulex, HP, IBM, Fujitsu, Cisco, Hitachi, and ATTO.

PCI IDs cover legacy SBUS/PCI devices through 64Gb FC adapters and FCoE OneConnect devices.

Model flags describe interrupt support (`INTx`, MSI, MSI-X), end-to-end authentication, GPIO LEDs, Oracle branding/exclusion, and unsupported status.

Chip flags distinguish DragonFly through Prism Gen7, plus grouped BE and Lancer-family masks.

SLI masks describe SLI2, SLI3, and SLI4 support.

Under `EMLXS_MODEL_DEF`, the file defines `emlxs_sbus_model[]`, `emlxs_pci_model[]`, and model counts. These tables include detailed descriptions and capabilities for each supported adapter.

## Research Notes

This header is hardware-enablement data for the FC storage driver. Matching PCI identity to model capabilities determines which firmware, SLI mode, interrupt type, authentication support, and FC/FCoE behavior the driver enables.
