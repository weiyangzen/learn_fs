# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs.h

## Purpose

`emlxs.h` is the main umbrella header for the Emulex LightPulse Fibre Channel/FCoE adapter driver.

## Main Interfaces

It defines `DRIVER_NAME` as `"emlxs"` and includes the driver’s OS, FCIO, hardware, mailbox, queue, IOCB, firmware, adapter database, message, event, thread, configuration, DFC library, FC, device, DFC, and extern headers.

Conditional includes add DH-CHAP authentication, COMSTAR target mode (`SFCT_SUPPORT`), SAN diagnostics, dump support, and Menlo support.

## Research Notes

This file contains no data structures of its own beyond the driver name. Its importance is dependency composition: including `emlxs.h` brings in the complete driver-private interface surface for the Emulex FCA, which is a storage transport driver backing FC/FCoE block devices.
