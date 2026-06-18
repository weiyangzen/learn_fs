# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc.h

## Purpose

`fc.h` is the global include wrapper for the Fibre Channel transport subsystem.

## Main Interfaces

The header only includes `<sys/fibre-channel/fc_types.h>` and provides the include guard `_FC_H`.

## Research Notes

This is an umbrella entry point used by Fibre Channel adapter drivers and transport consumers. Storage relevance comes from Fibre Channel being a block/SCSI transport layer rather than from any direct filesystem logic in this wrapper.
