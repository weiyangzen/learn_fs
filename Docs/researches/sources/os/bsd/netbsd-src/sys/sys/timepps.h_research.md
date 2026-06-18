# File Research: sources/os/bsd/netbsd-src/sys/sys/timepps.h

Read completely: 247 lines.

Defines the Pulse-Per-Second API and NetBSD PPS ioctl/kernel support.

Key elements:
- Declares PPS API version, `pps_handle_t`, `pps_seq_t`, `pps_timeu_t`, `pps_info_t`, and `pps_params_t`.
- Defines PPS capture, offset, wait/poll, echo, timestamp format, and kernel-consumer mode bits.
- Defines PPS ioctls for create, destroy, set/get params, get capabilities, fetch, and kernel clock binding.
- Kernel section defines reference event flags, `struct pps_state`, and `pps_capture`, `pps_event`, `pps_ref_event`, `pps_init`, and `pps_ioctl`.
- Userland section provides inline wrappers around ioctl for the PPS API.

Risks and notes:
- PPS is precision-time infrastructure; timestamp format and edge-selection mistakes affect clock discipline.
- Userland `time_pps_kcbind()` only accepts `PPS_TSFMT_TSPEC`.
