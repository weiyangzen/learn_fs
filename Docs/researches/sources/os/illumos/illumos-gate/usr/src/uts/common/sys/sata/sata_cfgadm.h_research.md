# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_cfgadm.h

## Role

Interface header between the SATA framework and the `cfgadm` plugin/devctl ioctl path.

## Key Elements

- `sata_cfga_apctl_t` enumerates attachment-point control subcommands:
  get AP type, model, firmware revision, serial number, reset port/device/all, port deactivate/activate, self-test, and device path lookup.
- `sata_ioctl_data_t` is the native ioctl payload with command, encoded port, size-query flag, buffer pointer, buffer size, and reserved argument.
- `sata_ioctl_data_32_t` provides 32-bit app / 64-bit kernel layout compatibility.
- Defines port-encoding masks and shift values matching SATA/SCSI target encoding for controller ports and port-multiplier ports.

## Dependencies and Coupling

Coupled to SATA devctl minor/target encoding from the framework and to cfgadm plugin expectations.

## Research Notes

The file contains no implementation, only ioctl command shape. Compatibility is explicit via the 32-bit structure.
