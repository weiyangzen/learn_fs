# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydevsw.h

Kernel TTY driver switch interface.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines callback typedefs for open, close, output wakeup, input wakeup, normal/control ioctl, parameter update, modem signal control, mmap, packet notification, destructor, and busy/drain status.
- Defines `struct ttydevsw` vtable with default flags, callbacks, and spare slots.
- Provides inline wrappers for each driver callback, asserting TTY locking where needed and checking that the TTY is not gone.
- Suppresses spurious output wakeups when no output is available and input wakeups when the input high-water mark remains set.

Dependencies:
- Depends on `struct tty`, `termios`, thread, vm offset/paddr/memattr types, and line discipline helpers from `sys/tty.h`.

Notable risks:
- Wrapper preconditions are part of the driver contract; callbacks invoked without required locks can race TTY teardown or queue state.
- Optional-looking vtable entries are called unconditionally by wrappers, so drivers must populate the methods they expose to common TTY code.
