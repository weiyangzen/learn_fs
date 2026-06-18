# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetpos.c

Read completely: 67 lines.

This file implements `fgetpos`. It captures relevant wide-character conversion state from the stream extension when wide mode is active, then stores the byte offset returned by `ftello`.

Important interactions: pairs with `fsetpos` and depends on `WCIO_GET` and `ftello`.

Security/reliability notes: returns nonzero when `ftello` fails; wide-state preservation is tied to stream read/write hook presence.
