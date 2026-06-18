# File Research: sources/os/bsd/dragonflybsd/sys/sys/poll.h

Public `poll(2)` and BSD `ppoll(2)` interface definitions.

Key responsibilities:
- Defines `nfds_t`.
- Defines `struct pollfd`.
- Defines requestable poll event bits and always-returned event bits.
- Defines BSD-visible `POLLSTANDARD` and `INFTIM`.
- Declares userland `poll()` and BSD `ppoll()` when visibility macros allow.

Important behavior:
- `POLLWRNORM` aliases `POLLOUT`.
- Comments note limited traditional distinction between priority/band events.
- Kernel inclusion avoids userland function declarations.

Dependencies:
- Userland declarations include `sys/cdefs.h`, and BSD-visible declarations include `signal.h` and `time.h`.

Notable risks:
- Event bit values are cross-platform ABI.
- Visibility macros determine which prototypes/constants userland sees.
