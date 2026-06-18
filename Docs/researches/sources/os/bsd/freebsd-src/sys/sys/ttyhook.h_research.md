# File Research: sources/os/bsd/freebsd-src/sys/sys/ttyhook.h

Kernel TTY hook interface for intercepting and injecting terminal traffic.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines hook callback typedefs for input character, bypass input, input completion, input poll, output injection, output capture, output poll, and close.
- Defines `struct ttyhook` vtable.
- Declares hook registration and unregistration.
- Provides helpers for hook softc access and testing whether a named hook exists.
- Provides inline wrappers for each hook callback, asserting TTY lock ownership and non-gone state where appropriate.

Dependencies:
- Depends on `struct tty`, proc, and TTY lock/teardown macros from `sys/tty.h`.

Notable risks:
- Hook callbacks run inside TTY data paths and can alter input/output behavior; registration must preserve lifetime and locking rules.
- `ttyhook_hashook()` only checks function pointer presence; callers must still hold appropriate TTY state before dispatch.
