# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xenoprof.h

Purpose: Xen public profiling ABI for XenOprofile/system-wide hardware counter profiling.

Key interfaces:
- `XENOPROF_*` commands from init/list setup/counter reservation/start/stop/shutdown/buffer/backtrace through AMD IBS support.
- `event_log`, `xenoprof_buf`, `xenoprof_init`, `xenoprof_get_buffer`, `xenoprof_counter`, `xenoprof_passive`, `xenoprof_ibs_counter`.

Integration notes: Depends on `xen.h`; profiling samples are delivered through shared per-VCPU buffers.

Risk/attention points: `xenoprof_buf` uses a one-element trailing `event_log` pattern; allocation sizing must account for actual sample capacity.
