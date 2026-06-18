# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_ioctl.h

## Summary
User/kernel ioctl ABI for the autofs daemon protocol.

## Main Responsibilities
- Defines control path `/dev/autofs`.
- Defines `struct autofs_daemon_request` containing request ID, map name, full path, prefix, key, and mount options.
- Defines `struct autofs_daemon_done` containing request ID, wildcard flag, error, and reserved fields.
- Defines `AUTOFSREQUEST` and `AUTOFSDONE` ioctl numbers.

## Important Behavior
`AUTOFSREQUEST` lets automountd fetch a pending request. `AUTOFSDONE` completes that request and tells the kernel whether wildcard entries may exist, controlling negative caching behavior.

## Risks
All strings are fixed `MAXPATHLEN` buffers. The daemon and kernel must preserve request IDs exactly or completions return `ESRCH` and waiters may time out.
