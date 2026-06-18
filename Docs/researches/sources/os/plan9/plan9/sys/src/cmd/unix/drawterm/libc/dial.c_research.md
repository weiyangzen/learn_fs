# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dial.c

This file implements Plan 9-style `dial`.

Key behavior:
- `dial` parses network address strings and either uses `/net/cs` through `csdial` or calls a clone/control/data endpoint directly.
- `call` opens clone, writes connect requests, opens data, and optionally returns control fd/path.
- `_dial_string_parse` decomposes network, address, service, and protocol fields.

Important details:
- Uses Plan 9 `/net` filesystem conventions even inside drawterm's hosted environment.
- Supports optional local address/control handling.
