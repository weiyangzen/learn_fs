# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consdev.h

`consdev.h` declares canonical pseudo-device paths and globals for real, virtual, workstation, mouse, keyboard, stdin, framebuffer, and diag console devices/vnodes. It defines console mode constants for firmware vs kernel framebuffer console.

It also defines console polled I/O ioctls, abort-enable ioctls, keyboard type ioctl, polled-I/O ABI version constants, key state enum, opaque argument pointer, and `cons_polledio` callback vector for entering/exiting, reading, and writing polled console I/O. Workstation-console framebuffer open/close ioctls are also included.
