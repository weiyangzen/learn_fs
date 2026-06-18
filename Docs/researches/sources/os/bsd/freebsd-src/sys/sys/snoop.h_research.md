# File Research: sources/os/bsd/freebsd-src/sys/sys/snoop.h

Snoop device ioctl constants.

Key responsibilities:
- Defines `SNPSTTY` to attach/set a snooped TTY using a file descriptor.
- Defines `SNPGTTY` to retrieve the associated TTY device.
- Defines special negative `FIONREAD` return values for snoop errors: overflow, TTY close, and detach.

Important patterns:
- Uses tty ioctl command group `'T'`.
- Error states are multiplexed through `FIONREAD` rather than a separate status ioctl.

Research relevance:
- Small legacy character-device ABI for TTY snooping behavior.
