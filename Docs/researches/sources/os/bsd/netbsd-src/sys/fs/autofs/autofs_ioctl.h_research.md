# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_ioctl.h

## Summary
Defines the user/kernel ioctl ABI for the AUTOFS daemon.

## Main Responsibilities
- Define control path `AUTOFS_PATH` as `/dev/autofs`.
- Define fixed maximum path length `AUTOFS_MAXPATHLEN`.
- Define `struct autofs_daemon_request` fields sent to automountd: id, map name, path, prefix, key, and options.
- Define `struct autofs_daemon_done` fields returned by automountd: id, wildcard flag, error, and reserved space.
- Define ioctl commands `AUTOFSREQUEST` and `AUTOFSDONE`.

## Risks
All string fields are fixed 256-byte arrays. Kernel and userland must preserve this ABI exactly.
