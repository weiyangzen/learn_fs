# File Research: sources/os/bsd/netbsd-src/sys/sys/radioio.h

## Purpose
Defines FM radio device ioctl ABI, frequency limits, capability bits, and status structure.

## Main API
- Frequency constants: `MIN_FM_FREQ`, `MAX_FM_FREQ`, `IF_FREQ`.
- Structure: `struct radio_info`.
- Capability bits: stereo/signal detection, mono control, hardware search/AFC, reference frequency, lock sensitivity, reserved/card type fields.
- Info bits: `RADIO_INFO_STEREO`, `RADIO_INFO_SIGNAL`.
- Ioctls: `RIOCGINFO`, `RIOCSINFO`, `RIOCSSRCH`.

## Dependencies
Includes `sys/param.h` and `sys/ioccom.h`.

## Risks and Notes
Frequency is in kHz. The capability field reserves bit ranges for card type and future use; drivers and tools must mask rather than compare the entire field blindly.
