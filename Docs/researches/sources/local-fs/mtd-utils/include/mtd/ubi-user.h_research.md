# File Research: sources/local-fs/mtd-utils/include/mtd/ubi-user.h

## Purpose
Defines the user-space UBI ioctl API.

## Key Elements
Documents attach/detach, volume create/remove/resize/rename/update, LEB erase/change/map/unmap/is-mapped, property setting, and block-device creation/removal. Defines ioctl numbers and request structs including `ubi_attach_req`, `ubi_mkvol_req`, `ubi_rsvol_req`, `ubi_rnvol_req`, `ubi_leb_change_req`, `ubi_map_req`, `ubi_set_vol_prop_req`, and `ubi_blkcreate_req`.

## Dependencies
Uses standard fixed-width integer types expected from the surrounding build environment.

## Behavior/Risks
Reserved padding fields must be zeroed by callers. Some fields such as `dtype` are obsolete but kept for old-kernel compatibility.
