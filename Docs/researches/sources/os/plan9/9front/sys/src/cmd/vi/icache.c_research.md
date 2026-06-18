# File Research: sources/os/plan9/9front/sys/src/cmd/vi/icache.c

`icache.c` is a stub instruction-cache module for the MIPS simulator. `icacheinit()` and `updateicache()` currently do nothing beyond accepting the address argument.

The rest of the simulator still has `Icache` state and calls `updateicache()` from instruction fetch when enabled, so this file preserves the interface for a cache model that is not implemented here.
