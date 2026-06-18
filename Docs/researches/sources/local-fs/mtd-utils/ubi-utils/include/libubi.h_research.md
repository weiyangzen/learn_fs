# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libubi.h

## Role
Primary public libubi API for UBI control, device/volume metadata, volume lifecycle, and volume I/O ioctls.

## Main Contents
- Defines `libubi_t`, `ubi_attach_request`, `ubi_mkvol_request`, `ubi_info`, `ubi_dev_info`, and `ubi_vol_info`.
- Declares library open/close and information lookup APIs.
- Declares attach/detach/remove, mkvol/rmvol/rnvol/rsvol, node probing, block-device creation/removal, update start, atomic LEB change, direct-write property, LEB unmap, and map check functions.

## Interfaces And Dependencies
- Includes `mtd/ubi-user.h` and `mtd/ubi-media.h`.
- Implemented by `libubi.c`.
- Consumed by tests and CLI tools.

## Notes
- Documents compatibility return value `1` from `ubi_attach` when `max_beb_per1024` is ignored by old kernels.
- API is a userspace wrapper over UBI sysfs and ioctls.
