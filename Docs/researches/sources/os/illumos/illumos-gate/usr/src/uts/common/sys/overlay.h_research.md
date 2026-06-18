# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay.h

## Purpose

`overlay.h` defines the public ioctl ABI for illumos overlay network devices. It exposes create/delete/property/activation/status operations and the fixed-size structures passed through the overlay control device.

## Ioctl ABI

The ioctl commands are `OVERLAY_IOC_CREATE`, `DELETE`, `PROPINFO`, `GETPROP`, `SETPROP`, `NPROPS`, `ACTIVATE`, and `STATUS`, all based on `OVERLAYIOC()`.

`overlay_ioc_create_t` supplies a datalink ID, virtual network ID, and encapsulation plugin name. Other structs identify a link for activation, deletion, property count, property info, property get/set, or status.

Property info includes property ID/name, type, permissions, default value/size, possible value size, and possible values. Property get/set uses link ID, ID/name, raw value buffer, and value size. Status returns `OVERLAY_I_OK` or `OVERLAY_I_DEGRADED` plus a status message.

## Dependencies

The header includes datalink ioctl definitions, MAC types, and `overlay_common.h` for property/status size constants and enums.

## Research Notes

This file is a user/kernel ABI. Changes to structure sizes, fixed buffer lengths, enum values, or ioctl numbers are compatibility-sensitive. Validation-sensitive fields include property sizes, encapsulation name length, and degraded status message handling.
