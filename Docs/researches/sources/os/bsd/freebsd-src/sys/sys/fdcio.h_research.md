# File Research: sources/os/bsd/freebsd-src/sys/sys/fdcio.h

## Purpose
Defines floppy disk controller ioctl structures, options, transfer rates, and common media geometry presets.

## Main Interfaces
- Formatting constants: `FD_FORMAT_VERSION`, `FD_MAX_NSEC`.
- `struct fd_formb` with nested hardware-format fields and ID fields.
- Convenience macros for nested format fields.
- `struct fd_type`: disk geometry and format parameters.
- `struct fdc_status`, `struct fdc_readid`.
- Drive type enum `fd_drivetype`.
- Ioctls: `FD_FORM`, `FD_GTYPE`, `FD_STYPE`, `FD_GOPTS`, `FD_SOPTS`, `FD_CLRERR`, `FD_READID`, `FD_GSTAT`, `FD_GDTYPE`.
- Drive options: `FDOPT_NORETRY`, `FDOPT_NOERRLOG`, `FDOPT_NOERROR`.
- Transfer rates: `FDC_500KBPS`, `FDC_300KBPS`, `FDC_250KBPS`, `FDC_1MBPS`.
- Common media presets: `FDF_3_*`, `FDF_5_*`.

## Dependencies And Integration
Includes `ioccom.h`; userland gets `sys/types.h`. Structures are designed to match legacy floppy hardware command formats.

## Risk Notes
`fd_form_data` layout is hardware-dependent and explicitly must not change. Ioctl compatibility and legacy geometry constants are the main hazards.
