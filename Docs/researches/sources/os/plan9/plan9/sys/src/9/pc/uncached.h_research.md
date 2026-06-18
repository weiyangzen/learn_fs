# File Research: sources/os/plan9/plan9/sys/src/9/pc/uncached.h

Purpose: PC-specific note for the port layer that uncached memory is not required on this architecture.

Content:
- The file contains only a comment stating that processor accesses, memory caches, and DMA are coherent on PC hardware, so uncached memory is unnecessary.

Dependencies and integration:
- Intended as an architecture override/header included by code that otherwise may need uncached memory handling on non-coherent platforms.

Risks and notes:
- The assumption is broad for the supported Plan 9 PC target. Drivers still use explicit `coherence()` where required for device-visible descriptor updates.
