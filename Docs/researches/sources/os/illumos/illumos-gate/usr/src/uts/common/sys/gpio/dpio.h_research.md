# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/dpio.h

## Role

`dpio.h` defines the user/kernel ABI for Digital Programmed I/O devices created from GPIOs.

## Key Interfaces and Data

- `DPIO_NAMELEN` is 64 for DPIO and controller names.
- `DPIO_IOC` is the ioctl command base.
- `dpio_output_t` defines write values: low, high, and disabled. Writes must be 4-byte `uint32_t` values.
- `dpio_input_t` defines read values: low and high. Reads must be 4-byte `uint32_t` values.
- `dpio_caps_t` advertises read, write, and poll capabilities.
- `dpio_flags_t` currently has `DPIO_F_KERNEL`.
- `DPIO_IOC_INFO` returns `dpio_info_t`: DPIO name, controller name, GPIO number, capabilities, flags, and padding.
- `DPIO_IOC_TIMING` returns `dpio_timing_t`: last input interrupt time and last write time.
- `DPIO_IOC_CUROUT` returns `dpio_curout_t`: current output state for the DPIO itself.

## Dependencies and Use

This header is usable by consumers of DPIO character devices and by kernel framework code. It intentionally documents read/write record sizes as part of the ABI.

## Research Notes

DPIO is a narrow file-descriptor interface over GPIO state, with ioctl metadata layered around simple 32-bit read/write values.
