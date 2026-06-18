# sources/test-tools/strace/bundled/linux/include/uapi/mtd/ubi-user.h

## Purpose
Defines the UBI userspace ioctl ABI for attaching/detaching MTD devices, managing UBI volumes, querying erase counters, performing volume updates, changing logical eraseblocks, setting volume properties, and creating or removing read-only ubiblock devices.

## Important APIs, Types, and Functions
Read coverage: 506 lines and 19974 bytes. Constants include `UBI_VOL_NUM_AUTO`, `UBI_DEV_NUM_AUTO`, `UBI_MAX_VOLUME_NAME`, `MAX_UBI_MTD_NAME_LEN`, `UBI_MAX_RNVOL`, UBI device/volume ioctl magic values, `UBI_DYNAMIC_VOLUME`, `UBI_STATIC_VOLUME`, `UBI_VOL_PROP_DIRECT_WRITE`, `UBI_VOL_SKIP_CRC_CHECK_FLG`, and `UBI_VOL_VALID_FLGS`. Control-device ioctls are `UBI_IOCATT` and `UBI_IOCDET`; UBI device ioctls are `UBI_IOCMKVOL`, `UBI_IOCRMVOL`, `UBI_IOCRSVOL`, `UBI_IOCRNVOL`, `UBI_IOCRPEB`, `UBI_IOCSPEB`, and `UBI_IOCECNFO`; volume ioctls are `UBI_IOCVOLUP`, `UBI_IOCEBER`, `UBI_IOCEBCH`, `UBI_IOCEBMAP`, `UBI_IOCEBUNMAP`, `UBI_IOCEBISMAP`, `UBI_IOCSETVOLPROP`, `UBI_IOCVOLCRBLK`, and `UBI_IOCVOLRMBLK`.

Structures are `ubi_attach_req`, `ubi_mkvol_req`, `ubi_rsvol_req`, `ubi_rnvol_req`, `ubi_ecinfo_req` with flexible erase-counter array, `ubi_leb_change_req`, `ubi_map_req`, `ubi_set_vol_prop_req`, and `ubi_blkcreate_req`. Many are packed and contain reserved padding that callers must zero.

## Control Flow
UBI control-device flow attaches an MTD device with `UBI_IOCATT` and detaches with `UBI_IOCDET`. UBI device flow creates, removes, resizes, and atomically renames volumes, scrubs PEBs, and reads erase counters. Volume-device flow starts a full-volume update by declaring image size with `UBI_IOCVOLUP` and then writing exactly that many bytes, performs atomic LEB change with a similar write-after-ioctl sequence, maps or unmaps LEBs, checks mapping state, sets direct-write property, and creates/removes a read-only block device.

## State and Persistence Behavior
UBI operations mutate persistent flash metadata: attached device identity, volume table entries, volume names and IDs, volume sizes and types, static-volume CRC policy, logical-to-physical eraseblock mappings, erase counters, update transactions, and ubiblock exposure. Some operations are explicitly transactional, especially atomic volume rename and atomic LEB change. `UBI_IOCEBUNMAP` is asynchronous with respect to physical erase completion, so an unclean reboot can leave the LEB mapped again.

## Dependencies and Integration Points
Direct include is `<linux/types.h>`. In strace it supports symbolic decoding of UBI ioctl calls and packed request payloads. Kernel and userspace integration points include MTD devices, UBI core, UBIFS, ubiblock, ubiattach/ubidetach/ubimkvol/ubirmvol/ubirsvol/ubirename/ubiupdatevol/ubinfo, boot-time volume handling, and NAND wear-leveling/scrubbing.

## Risks and Edge Cases
Risks include destructive attach/detach and volume changes, power-cut behavior, packed ABI layout, fixed maximum names and rename count, zeroing padding for forward compatibility, `UBI_IOCVOLUP` taking a pointer to `__s64` despite ioctl encoding constraints on 32-bit systems, obsolete `dtype` fields that should be set to 3 for old kernels, autoreserved bad-block pool settings, fastmap disable semantics, skip-CRC use only when another integrity mechanism exists, and flexible-array erase-counter allocation sizing.

## Test Signals
Strace tests should cover all UBI ioctl names and request structures, including packed fields and flexible `ubi_ecinfo_req` output. Behavioral signals include nandsim-based attach/detach, create/remove/resize, atomic multi-volume rename with power-cut simulation, interrupted volume update, LEB map/unmap/change/is-mapped, erase-counter reads with bad/unknown blocks, direct-write property setting, scrub requests, and ubiblock create/remove.
