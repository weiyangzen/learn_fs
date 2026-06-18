# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipd.h

This private header defines the interface between the `ipd` driver and `ipdadm`.

Purpose:
- `ipd` appears to inject IP disruption/perturbation behavior per zone: corrupt, delay, and drop.

Key definitions:
- Device path: `IPD_DEV_PATH` as `/dev/ipd`.
- `IPD_MAX_DELAY` is 10000 microseconds.
- `ipd_ioc_perturb_t` contains zone ID and argument.
- `ipd_ioc_info_t` contains zone ID and current corrupt/drop/delay settings.
- `_KERNEL` 32-bit list form: `ipd_ioc_list32_t`.
- `ipd_ioc_list_t` contains count and pointer to info array.
- Flags: `IPD_CORRUPT`, `IPD_DELAY`, `IPD_DROP`.
- Ioctl command base and commands: `IPDIOC_CORRUPT`, `IPDIOC_DELAY`, `IPDIOC_DROP`, `IPDIOC_LIST`, `IPDIOC_REMOVE`.

Relevance:
- Network fault-injection/control utility. Relevant to testing networked storage behavior but not a filesystem implementation.
