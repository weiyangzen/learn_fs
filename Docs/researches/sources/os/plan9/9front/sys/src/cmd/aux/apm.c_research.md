# File Research: sources/os/plan9/9front/sys/src/cmd/aux/apm.c

Role: User-space APM service exposing BIOS/APM power status and controls as a 9P filesystem.

Main components:
- Low-level APM wrappers call `/dev/apm` or `#P/apm` by writing and reading `Ureg` structures. `apmcall` serializes access with `apmlock`.
- `Apm` stores file descriptor, version, AC status, battery count, capabilities, and up to four `Battery` records.
- 9P files are `/`, `event`, `battery`, and `ctl`.

Filesystem behavior:
- `battery` reads lines of `status percent time` for detected batteries.
- `ctl` reads AC/capability/power-state information and accepts commands such as `display standby`, `system on`, `network disable`, and `pcmcia suspend`.
- `event` supports blocking reads from an internal event queue populated by `eventwatch`, with Tflush interruption support.

Startup:
- Validates APM version >= 1.2, reads capabilities, performs installation check, calls CPU idle, then mounts at `/mnt/apm` by default.
- Options include debug, chatty9p, no polling, custom device, mount point, and srv name.

Notes:
- Suspend is available through generic command handling but comments warn it can disturb cycle counters and PCMCIA ethernet cards.
- Error strings translate APM carry-flag codes into readable messages.
