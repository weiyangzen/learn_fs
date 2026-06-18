# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sgpio.h

## Role

Private NVIDIA SGPIO register and bitfield definition header for `nv_sata`. It describes the NVIDIA SGPIO command/status register, control block, configuration registers, and LED transmit-register encodings.

## Key Elements

- Defines SGPIO PCI config offsets `SGPIO_CSRP` and `SGPIO_CBP`.
- Defines SGPIO command/status register masks and helpers for command, command status, sequence bit, and SGPIO state.
- Defines command values for reset, read parameters, read data, and write data.
- `nv_sgp_cb_t` models the SGPIO control block, including scratch registers, NVIDIA configuration register, SGPIO configuration registers, GP transmit/receive config, and SGPIO transmit registers.
- Defines NVIDIA-specific configuration fields for initiator count, control-block size, and control-block version.
- Defines generic SGPIO CR0 fields for version, enable, GP/config register count, and supported drive count.
- Under `SGPIO_BLINK`, defines blink generator rates and blink-mode LED encodings.
- Provides macros for packing/unpacking per-drive activity, locate, and error indicator fields in SGPIO transmit registers.

## Dependencies and Coupling

Used by `nv_sata` only when SGPIO support is compiled in. The layout differs between `__amd64` and non-amd64 for the scratch-register representation, preserving expected hardware layout.

## Research Notes

The header is exclusively register vocabulary. Comments note that NVIDIA-documented blink generator values did not actually produce blinking LEDs, so blink support is conditional and likely experimental or disabled in normal builds.
