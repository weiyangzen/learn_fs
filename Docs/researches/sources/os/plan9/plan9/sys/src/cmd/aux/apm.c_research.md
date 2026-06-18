# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/apm.c

This file implements a 9P filesystem interface to PC APM power-management BIOS calls.

Key behavior:
- Opens `/dev/apm`, `#P/apm`, or a user-specified APM device and issues BIOS-style calls by reading/writing `Ureg`.
- Exposes a mounted namespace containing `event`, `battery`, and `ctl`.
- `battery` reports per-battery status, percentage, and remaining time.
- `ctl` reports AC status, capabilities, and device power states; writes issue commands such as `enable`, `disable`, `standby`, `on`, and `suspend`.
- A background event polling path queues APM notifications for blocking reads of `event`.

Important details:
- Serializes APM calls with `apmlock`.
- Requires APM version 1.2 or newer.
- Event reads are cancellable through 9P flush handling.
- Supports pipe/stdin mode with `-i`, mount point with `-m`, service name with `-s`, no-poll mode with `-P`, and debug flags.

Filesystem relevance:
- Direct: a synthetic 9P filesystem mapping firmware power state and events into ordinary Plan 9 files.
