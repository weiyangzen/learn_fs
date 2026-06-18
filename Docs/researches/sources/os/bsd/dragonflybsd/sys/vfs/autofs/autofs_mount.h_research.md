# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_mount.h

## Summary
Mount argument ABI for autofs.

## Main Responsibilities
- Defines `struct autofs_mount_info` with user pointers for map source, master options, and master prefix.

## Important Behavior
`autofs_mount()` copies this structure from userland and then copies each pointed-to string separately.

## Risks
The structure contains userland pointers, not embedded strings. Kernel mount code must use `copyin`/`copyinstr` carefully and handle partial failures.
