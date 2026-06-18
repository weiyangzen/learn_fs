# File Research: sources/os/linux/linux-stable/fs/dlm/recoverd.h

## Purpose
`recoverd.h` declares per-lockspace recovery-thread lifecycle helpers.

## Exports
- `dlm_recoverd_start()`
- `dlm_recoverd_stop()`
- `dlm_recoverd_suspend()`
- `dlm_recoverd_resume()`

## Notes
Suspend/resume is used by membership stop logic to ensure recoverd has noticed abort flags before state is reset.
