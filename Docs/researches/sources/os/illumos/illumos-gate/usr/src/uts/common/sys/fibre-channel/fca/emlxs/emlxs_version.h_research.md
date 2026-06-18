# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_version.h

## Purpose

Defines version, revision, copyright, and display-label strings for the `emlxs` driver and firmware.

## Main Definitions

- `EMLXS_COPYRIGHT`: Emulex copyright string.
- `EMLXS_VERSION`: `"2.80.9.0"`.
- Date components:
  - minute `50`
  - hour `16`
  - day `16`
  - month `01`
  - year `2024`
- `EMLXS_REVISION`: concatenates date components as `YYYY.MM.DD.HH.MM`.
- `EMLXS_NAME`: combines `DRIVER_NAME`, date, and version for FCA naming.
- `EMLXS_LABEL`: combines `VERSION`, `EMLXS_ARCH`, `MACH`, and `EMLXS_VERSION`.
- `EMLXS_FW_NAME`: combines `DRIVER_NAME`, date, and version for firmware naming.

## Integration Notes

This header expects macros such as `DRIVER_NAME`, `VERSION`, `EMLXS_ARCH`, and `MACH` to be defined by including context or build configuration.

## Risks and Gotchas

- The string concatenation relies on adjacent string literals and macro expansion. Missing build macros will cause compile failures.
- Version date and semantic version are independent constants; release tooling must update both consistently.
