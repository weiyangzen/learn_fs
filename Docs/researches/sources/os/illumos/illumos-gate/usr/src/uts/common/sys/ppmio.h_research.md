# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmio.h

## Purpose
Defines platform power-management driver ioctl commands and user/kernel payload structures for querying and controlling power domains and device/domain mappings.

## Main Interfaces
- Ioctls:
  - `PPMIOCSET`
  - `PPMIOCGET`
  - `PPMGET_DPWR`
  - `PPMGET_DOMBYDEV`
  - `PPMGET_DEVBYDOM`
  - x86 test-only `PPMGET_NORMAL`, `PPMSET_NORMAL`
- Payloads:
  - `ppmreq_t`
  - `struct ppm_dpwr`
  - `struct ppm_bydev`
  - `struct ppm_bydom`
  - `struct ppm_norm`
- 32-bit variants:
  - `ppm_dpwr32`
  - `ppm_bydev32`
  - `ppm_bydom32`
  - `ppm_norm32`
- Power/LED values:
  - `PPMIO_POWER_OFF`
  - `PPMIO_POWER_ON`
  - `PPMIO_LED_BLINKING`
  - `PPMIO_LED_SOLIDON`
  - compatibility aliases `PPM_IDEV_POWER_OFF`, `PPM_IDEV_POWER_ON`

## Dependencies And Relationships
Includes `sys/types.h`. Consumed by PPM driver ioctl paths; `ppmvar.h` defines the driver-private domain/control structures.

## Research Notes
Some ioctls are documented as legacy or test-only. Pointer-bearing structures have explicit ILP32 kernel views.
