# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm.h

This header defines the public user/kernel ABI and kernel driver interface for DDI UFM, the Unified Firmware Management facility. It exposes `/dev/ufm`, UFM interface versioning, UFM ioctls, packed nvlist schema keys, capability bits, slot attributes, ioctl payload structures, and kernel driver callbacks.

The ioctl family is based on `UFM_IOC`: `UFM_IOC_GETCAPS`, `UFM_IOC_REPORTSZ`, `UFM_IOC_REPORT`, and `UFM_IOC_READIMG`. The current version is `1`. Capabilities include reporting UFM information and reading firmware images.

User ABI structures include `ufm_ioc_getcaps_t`, `ufm_ioc_bufsz_t`, `ufm_ioc_report_t`, and `ufm_ioc_readimg_t`, each carrying version and device path fields. Kernel-only 32-bit forms are provided for buffer size, report, and read-image payloads. The read-image 32-bit form is packed to preserve ABI layout.

The report format is a packed nvlist. Top-level data contains `ufm-images`; each image can contain description, optional image misc nvlist, and an array of slot nvlists. Slot data includes version, attributes, optional misc nvlist, and optional image size. Attributes include readable, writeable, active, and empty, with `DDI_UFM_ATTR_MAX` as the valid mask.

Kernel driver-facing declarations define opaque handle/image/slot types and `ddi_ufm_ops_t`: callbacks for image count, filling image metadata, filling slot metadata, getting capabilities, and reading an image. Drivers call `ddi_ufm_init`, `ddi_ufm_update`, and `ddi_ufm_fini`, and use setters in fill callbacks to populate images and slots.

Research notes:
- This header is both user ABI and kernel DDI interface.
- Packed nvlist key names are ABI-visible and must be preserved.
- `UFM_IOC_MAX` is currently set to `UFM_IOC_REPORT`, even though `UFM_IOC_READIMG` exists; consumers should verify ioctl range logic in implementation.
