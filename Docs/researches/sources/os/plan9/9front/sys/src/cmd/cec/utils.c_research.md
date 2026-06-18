# File Research: sources/os/plan9/9front/sys/src/cmd/cec/utils.c

Console raw-mode and packet dump utilities for CEC.

Key behavior:
- `rawon` opens `/dev/consctl` and writes `rawon` unless running as a posted service.
- `rawoff` closes the console control fd unless running as a service.
- `dump` formats bytes in 16-byte rows as hex for diagnostics.

Dependencies:
- Includes Plan 9 libc and `cec.h`.
- Uses external `svc` to skip console manipulation for service mode.

Research notes:
- `format` uses a static line buffer, so dump output is simple diagnostic output rather than a reusable formatter.
