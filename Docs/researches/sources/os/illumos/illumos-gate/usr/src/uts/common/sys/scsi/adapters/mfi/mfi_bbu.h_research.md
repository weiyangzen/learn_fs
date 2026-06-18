# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_bbu.h

## Role

MFI battery backup unit definition header.

## Key Elements

- Defines packed BBU capacity, design information, iBBU state, traditional BBU state, combined BBU status, and BBU properties structures.
- `mfi_bbu_capacity_t` reports charge, capacity, runtime, cycle count, error, and alarm thresholds.
- `mfi_bbu_design_info_t` reports manufacturing date, design capacity/voltage, serial, manufacturer/device/chemistry strings, and manufacturing data.
- `mfi_ibbu_state_t` and `mfi_bbu_state_t` model state details for intelligent BBU and regular BBU variants.
- `mfi_bbu_status_t` includes BBU type, voltage/current/temperature, state bitfield, padding, and a union for BBU/iBBU state.
- `mfi_bbu_properties_t` includes auto-learn period, next learn time, delay interval, learn mode, and BBU mode.
- Compile-time assertions enforce firmware-visible sizes.

## Dependencies and Coupling

Includes `mfi.h` for shared typedefs and MFI constants. Used with BBU DCMDs defined in the core header.

## Research Notes

The BBU status union lets the same 64-byte status block carry either classic BBU or iBBU-specific details after common health and sensor fields.
