# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/icache.c

Purpose: Placeholder instruction-cache simulation hooks.

Key behavior:
- `icacheinit` is empty.
- `updateicache` accepts an address and marks it used but performs no work.

Dependencies:
- Included by the simulator memory fetch path when `icache.on` is set.

Notable details:
- Instruction cache simulation is effectively disabled in this file.
