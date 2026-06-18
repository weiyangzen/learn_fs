# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ioctl.h

## Role

Shared MFI ioctl interface definition used by MFI-family drivers and closed-source management utilities.

## Key Elements

- Defines ioctl signatures for driver, firmware, and AEN requests.
- Defines common driver ioctl control codes for driver version, PCI information, and MRRAID statistics.
- Defines fixed sense length for ioctl payloads.
- Packed structures:
  `mfi_drv_ver_t` for driver signature/OS/driver version/release strings.
  `mfi_pci_info_t` for bus/device/function/interrupt, PCI config header, capability bytes, and reserved space.
  `mfi_ioctl_t` for the external ioctl payload: version, controller ID, signature, control code, embedded `mfi_frame_t`, SGL, sense buffer, and trailing data array.

## Dependencies and Coupling

Includes DDI/cred/file/errno headers and `mfi.h`. Comments state the interface must not be changed because closed-source utilities such as StorCLI depend on it.

## Research Notes

This is an ABI-sensitive header. The trailing `ioc_data[0]` supports variable-sized firmware/user data transfers after the fixed ioctl header.
