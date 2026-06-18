# sources/test-tools/strace/bundled/linux/include/uapi/linux/ptp_clock.h

## Purpose

Defines the character-device ioctl ABI for Precision Time Protocol hardware clocks. strace uses it to decode `PTP_*` ioctl commands, timestamp request structures, pin configuration, and external timestamp events.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` and `linux/types.h`. It exports feature and validation flags for external timestamp and periodic output requests, `struct ptp_clock_time`, `ptp_clock_caps`, `ptp_extts_request`, `ptp_perout_request`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `enum ptp_pin_function`, `ptp_pin_desc`, and `ptp_extts_event`. Ioctls are encoded under `PTP_CLK_MAGIC`, including original and `*2` variants for caps, external timestamp, per-out, PPS, system offset, pin get/set, precise/extended offsets, mask operations, and cycle-based offset ioctls.

## Control Flow, State, and Integration

Runtime flow is device-fd ioctl based. Userspace queries clock capabilities, configures external timestamp or periodic output channels, requests cross timestamp samples, configures pins, and reads timestamp events. State persists in the kernel PTP clock device: enabled channels, pin function mappings, PPS state, masks, and hardware clock capabilities.

## Risks and Test Signals

Risks include accepting invalid v1 flags, mishandling the `ptp_perout_request` unions where `start` and `phase` depend on `PTP_PEROUT_PHASE`, and missing `clockid` reuse in `ptp_sys_offset_extended`. Test signals include ioctl decode tests for original and `*2` command names, flag validation display, sample-array sizing at `PTP_MAX_SAMPLES`, and external timestamp event formatting.
