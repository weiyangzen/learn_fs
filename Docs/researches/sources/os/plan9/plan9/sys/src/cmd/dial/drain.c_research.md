# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/drain.c

This file implements a tiny stdin-draining helper.

Key behaviors:
- Sets a short 100 ms alarm.
- Reads from stdin into a 256-byte buffer until read returns EOF/error or the alarm terminates/interrupts the read.
- Exits with status `0`.

Notable implementation details:
- A `ding()` note handler is defined to continue on alarm notes, but `main()` does not install it with `notify()`.
- In practice the helper is intended to consume any immediately pending input from a pipeline or modem connection.
