# File Research: sources/os/linux/linux-stable/fs/dlm/util.c

## Purpose
`util.c` provides wire-stable errno translation for DLM protocol messages.

## Behavior
Higher errno values differ across architectures, so DLM maps selected Linux errno values to fixed numeric DLM errno constants before sending them on the wire:
- `EDEADLK`
- `EBADR`
- `EBADSLT`
- `EPROTO`
- `EOPNOTSUPP`
- `ETIMEDOUT`
- `EINPROGRESS`

`to_dlm_errno()` converts Linux errno values to DLM wire values. `from_dlm_errno()` converts them back.

## Notes
Unlisted errno values pass through unchanged.
