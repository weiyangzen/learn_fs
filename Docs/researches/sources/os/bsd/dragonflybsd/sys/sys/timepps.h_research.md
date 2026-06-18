# File Research: sources/os/bsd/dragonflybsd/sys/sys/timepps.h

Pulse-per-second timing API definitions and ioctl wrappers.

Key contents:
- Defines PPS API version 1.
- Defines PPS handle and sequence types.
- Defines NTP fixed-point timestamp type `ntp_fp_t`.
- Defines `pps_timeu_t`, carrying either `timespec` or NTP fixed-point time.
- Defines `pps_info_t` and `pps_params_t`.
- Defines PPS capture, offset, echo, wait/poll, timestamp format, and kernel-consumer constants.
- Defines ioctl payload structs:
  - `pps_fetch_args`
  - `pps_kcbind_args`
- Defines ioctl commands:
  - create/destroy
  - set/get params
  - get capabilities
  - fetch
  - kernel-consumer bind
- Kernel side:
  - defines `struct pps_state`
  - declares `pps_event`, `pps_init`, `pps_ioctl`, and `hardpps`
- User side:
  - inline wrappers `time_pps_create`, `destroy`, `setparams`, `getparams`, `getcap`, `fetch`, and `kcbind`

Important behavior:
- `time_pps_create` stores the file descriptor itself as the handle.
- `time_pps_fetch` uses `(-1, -1)` timeout when caller passes `NULL`.
- Kernel PPS state stores parameter/current info, kernel consumer mode, capabilities, and recent sysclock counts.

Research notes:
- This header bridges userland PPS consumers, device ioctl implementations, and kernel hard-PPS discipline.
