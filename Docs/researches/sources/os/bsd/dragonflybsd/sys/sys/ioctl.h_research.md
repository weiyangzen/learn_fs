# File Research: sources/os/bsd/dragonflybsd/sys/sys/ioctl.h

`ioctl.h` is an umbrella public ioctl header. If included in the kernel, it emits a warning advising kernel code to include specific `xxxio.h` headers instead.

It includes `sys/filio.h`, `sys/sockio.h`, and `sys/ttycom.h`.

The file contains no command definitions of its own beyond aggregating common file, socket, and tty ioctl definitions for userland consumers.
