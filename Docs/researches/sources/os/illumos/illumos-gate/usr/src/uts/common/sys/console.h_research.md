# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/console.h

`console.h` defines console ioctl commands for fetching terminal type and device, plus result structures and 32-bit forms. `MAX_TERM_TYPE_LEN` limits terminal type strings.

Kernel declarations provide console size lookup, formatted printing, raw string output, line input, character input, enter/exit handling, and globals for the console vnode and console taskq.
