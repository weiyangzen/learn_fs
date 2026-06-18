# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkio.h

This header defines the disk ioctl ABI, disk geometry/info structures, media metadata, write-cache controls, partition queries, firmware update structures, directed read structures, disk ID structures, and free/discard ioctls. It includes `sys/dklabel.h`.

`dk_cinfo` reports controller name/type/flags, controller and unit numbers, partition, max transfer, and slave number. Controller type constants include old controller classes, SCSI, IDE/direct, PCMCIA, virtual block device, and generic block device. Controller flags describe formatting and bad-sector behavior.

Geometry and partition structures include `dk_allmap`, 32-bit map form, and `dk_geom`. The ioctl namespace is `DKIOC`, with commands for geometry, info, eject, VTOC/extVTOC get/set, write-cache flush/get/set, physical/virtual geometry, lock/unlock, media state/removable/hotpluggable/solid-state, defect lists, partition info, erase-bypass controls, media info, mboot get/set, temperature, read-only state, EFI get/set, and historical partition query aliases.

`dk_callback` supports asynchronous write-cache flushing in kernel `FKIOCTL` mode. `dkio_state` reports inserted/ejected/gone state. `dk_temperature`, `dk_minfo`, `dk_minfo_ext`, and 32-bit media info forms describe media type, block size, capacity, and logical/physical block geometry. Media type constants cover optical, fixed disk, floppy, ZIP, and JAZ classes.

Volume capability and directed mirror read support use `volcap_t`, `vol_directed_rd_t`, and 32-bit form, with ABR/DMR capability bits and directed-read status bits. Disk identity support uses `dk_disk_id_t` with ATA/SCSI strings and type flags. Firmware update support uses `dk_updatefw_t` and 32-bit form plus temporary/permanent firmware type constants.

Free/discard support defines `DKIOCFREE`, `DF_WAIT_SYNC`, extent and list structures (`dkioc_free_list_ext_t`, `dkioc_free_list_t`), size macro `DFL_SZ`, and `DKIOC_CANFREE`.

Research notes:
- This is a large user/kernel ABI header; structure layout and ioctl numbers are externally visible.
- Some ioctl numbers overlap by design/history: `DKIOCSETEXTPART` and `DKIOC_GETDISKID` both use `DKIOC|46`.
- Several older commands are obsolete but retained for compatibility.
- `dkioc_free_util.h` provides kernel copyin/iteration helpers for `DKIOCFREE`.
