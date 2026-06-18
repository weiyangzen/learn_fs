# File Research: sources/os/bsd/openbsd-src/sys/sys/termios.h

Defines the POSIX/BSD terminal attribute ABI: control-character indexes, input/output/control/local flags, baud constants, and `struct termios`. Visibility is controlled by `__BSD_VISIBLE`, `__XPG_VISIBLE`, and `_KERNEL`.

Userland declarations include `tcgetattr`, `tcsetattr`, `tcdrain`, `tcflow`, `tcflush`, `tcsendbreak`, speed helpers, `tcgetsid`, and BSD helpers `cfmakeraw`/`cfsetspeed`. Under BSD visibility it also includes `sys/ttycom.h` and, after the include guard, `sys/ttydefaults.h`, so default terminal state macros are available to BSD consumers.
