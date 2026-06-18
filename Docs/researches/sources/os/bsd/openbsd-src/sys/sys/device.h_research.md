# File Research: sources/os/bsd/openbsd-src/sys/sys/device.h

This header defines OpenBSD autoconfiguration and device core structures.

Key definitions:
- Device classes: `DV_DULL`, `DV_CPU`, `DV_DISK`, `DV_IFNET`, `DV_TAPE`, `DV_TTY`.
- Power/lifecycle actions: `DVACT_DEACTIVATE`, `QUIESCE`, `SUSPEND`, `RESUME`, `WAKEUP`, `POWERDOWN`.
- Core structs: `struct device`, `struct cfdata`, `struct cfattach`, `struct cfdriver`, `struct pdevinit`.
- Config states: `FSTATE_NOTFOUND`, `FOUND`, `STAR`, disabled variants.
- Driver modes: `CD_INDIRECT`, `CD_SKIPHIBERNATE`, `CD_COCOVM`.

Kernel APIs:
- Autoconf: `config_init`, `config_search`, `config_found_sm`, `config_rootfound`, `config_scan`, `config_attach`, `config_detach`, suspend/resume/deactivate helpers, deferred mountroot helpers.
- Sleep/resume: `request_sleep`, `sleep_state`, `gosleep`, `suspend_finish`, `resuming`.
- Device lookup/ref/root: `device_mainbus`, `device_lookup`, `device_ref`, `device_unref`, `findblkmajor`, `getdisk`, `parsedisk`, `setroot`.
- Firmware: `loadfirmware`, with `FIRMWARE_MAX`.

Risk notes:
- `struct device` and config structs are central kernel ABI-internal contracts for every driver.
- `CD_COCOVM` allows devices in confidential-computing VMs, so mode flags have security/platform policy meaning.
