# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mouse.c

This file probes and configures serial and PS/2 mouse devices.

Key behavior:
- Writes to `/dev/mousectl` to configure the detected mouse type.
- For serial mice, opens `#t/eiaNctl` and `#t/eiaN`, toggles RTS/DTR, tests protocol responses, and sets line parameters.
- Detects Microsoft-compatible, Logitech/type C, and type W mice.
- Can change baud rates where supported.
- Supports explicit defaults, debug tracing, and no-set mode.

Important details:
- Uses alarms to bound serial reads/writes.
- Retries detection up to six times.
- Type W 9600 baud is only used when receiver configuration indicates support.
- `ps2*` arguments are passed directly to `/dev/mousectl`.

Filesystem relevance:
- Indirect: configures Plan 9 device files for mouse input.
