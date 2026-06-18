# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/testld.c

Role: Load-test utility for flashfs images.

Behavior:
- Requires `-n nsect -z sectsize -f file`.
- Validates sector count and size are reasonable.
- Allocates sector buffer, initializes backend read-only style, initializes entries, and calls `loadfs(1)`.

Use:
- Checks whether an existing flashfs image can be loaded/replayed without mounting it for service.
