# File Research: sources/os/linux/linux/fs/dlm/util.c

## Role

`util.c` translates Linux errno values to stable DLM wire errno values and back.

## Behavior

Higher Linux errno numbers vary across architectures, so DLM uses fixed numeric values for selected errors on the wire:
- `EDEADLK`
- `EBADR`
- `EBADSLT`
- `EPROTO`
- `EOPNOTSUPP`
- `ETIMEDOUT`
- `EINPROGRESS`

`to_dlm_errno()` maps kernel errors to fixed negative wire values. `from_dlm_errno()` maps them back to local kernel errno values.

## Research Notes

Read completely. This file protects cross-architecture protocol compatibility for recovery and lock messages.
