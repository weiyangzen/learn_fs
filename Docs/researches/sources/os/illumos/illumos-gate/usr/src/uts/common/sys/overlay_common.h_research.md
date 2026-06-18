# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_common.h

## Purpose

`overlay_common.h` contains small shared overlay networking definitions used by both public overlay ioctls and internal overlay implementation/plugin code.

## Definitions

`overlay_target_mode_t` distinguishes no target, point target, and dynamic target modes. `overlay_plugin_dest_t` describes the destination tuple fields required by an encapsulation plugin: Ethernet, IP, port, or mask combinations.

`overlay_prop_type_t` defines property payload types: signed integer, unsigned integer, IP address (`sinaddr6` per comment), and fixed-size string. `overlay_prop_prot_t` defines required/read/write permission flags and combined masks.

The fixed ABI sizes are `OVERLAY_PROP_NAMELEN` 64, `OVERLAY_PROP_SIZEMAX` 256, and `OVERLAY_STATUS_BUFLEN` 256.

## Research Notes

This file is ABI glue. The important constraints are stable enum values and fixed property/status buffer sizes. Property permission masks are bitfields, so validation should mask unknown bits with `OVERLAY_PROP_PERM_MASK`.
